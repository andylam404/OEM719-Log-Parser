from .log_reader import LogReader
from .timestamp_extractor import TimestampExtractor
from .frequency_filter import FrequencyFilter
from .duration_limiter import DurationLimiter
from .csv_writer import CSVWriterManager
from .message_parsers import (
    BestXYZParser,
    TimeAParser,
    PSRDOPAParser,
    HWMonitorAParser,
    GPGSVParser
)


class OEM719Parser:
    def __init__(self, input_file: str, output_dir: str,
                 offset_bytes: int = 1000000,
                 max_duration_seconds: int = 30,
                 frequency_hz: float = 5.0):
        self.input_file = input_file
        self.output_dir = output_dir
        self.offset_bytes = offset_bytes

        self.timestamp_extractor = TimestampExtractor()
        self.frequency_filter = FrequencyFilter(frequency_hz=frequency_hz)
        self.duration_limiter = DurationLimiter(max_duration_seconds=max_duration_seconds)

        self.parsers = {
            'BESTXYZA': BestXYZParser(),
            'TIMEA': TimeAParser(),
            'PSRDOPA': PSRDOPAParser(),
            'HWMONITORA': HWMonitorAParser(),
            'GPGSV': GPGSVParser()
        }

    def parse(self):
        print(f"Starting OEM719 log parser...")
        print(f"Input file: {self.input_file}")
        print(f"Output directory: {self.output_dir}")

        with LogReader(self.input_file, self.offset_bytes) as reader:
            print("Seeking to start position (1MB offset or GPS lock)...")
            has_lock = reader.seek_to_start_position()

            if has_lock:
                print("Found GPS lock, starting parsing...")
            else:
                print("Warning: No GPS lock found after 1MB offset, continuing anyway...")

            with CSVWriterManager(self.output_dir) as csv_manager:
                line_count = 0
                line_buffer = []

                for line in reader.read_lines():
                    line_count += 1

                    self.frequency_filter.wait_for_next_sample()

                    timestamp = self.timestamp_extractor.get_current_timestamp()

                    if not self.duration_limiter.is_started():
                        self.duration_limiter.start()

                    if '#BESTXYZA' in line:
                        self._process_bestxyz(line, timestamp, csv_manager)

                    elif '#TIMEA' in line:
                        self._process_timea(line, timestamp, csv_manager)

                    elif '#PSRDOPA' in line:
                        self._process_psrdopa(line, timestamp, csv_manager)

                    elif '#HWMONITORA' in line:
                        self._process_hwmonitora(line, timestamp, csv_manager)

                    elif '$GPGSV' in line:
                        import re
                        match = re.match(r'\$GPGSV,(\d+),', line)
                        total_sentences = int(match.group(1)) if match else 1

                        line_buffer = [line]
                        for _ in range(total_sentences - 1):
                            try:
                                next_line = next(reader.read_lines())
                                if '$GPGSV' in next_line:
                                    line_buffer.append(next_line)
                                    line_count += 1
                            except StopIteration:
                                break

                        consumed = self._process_gpgsv(reader, line_buffer, timestamp, csv_manager)

                        combined_gpgsv = '\n'.join(line_buffer)
                        csv_manager.write_row('RAW', [timestamp, f'"{combined_gpgsv}\n"'])

                        continue

                    csv_manager.write_row('RAW', [timestamp, f'"{line}\n"'])

                    if self.duration_limiter.has_expired():
                        print(f"\nReached {self.duration_limiter.get_elapsed_seconds():.1f}s duration limit")
                        break

                    if line_count % 1000 == 0:
                        elapsed = self.duration_limiter.get_elapsed_seconds()
                        print(f"Processed {line_count} lines... (elapsed: {elapsed:.1f}s)")

                print("\nParsing complete!")
                print(f"Total lines processed: {line_count}")
                print(f"\nMessages written:")
                for msg_type, count in csv_manager.get_all_counts().items():
                    print(f"  {msg_type}: {count}")
                print(f"\nOutput files created in: {self.output_dir}")

    def _process_bestxyz(self, line: str, timestamp: str, csv_manager: CSVWriterManager):
        row = self.parsers['BESTXYZA'].parse(timestamp, line)
        if row and self.frequency_filter.should_record('BESTXYZ'):
            csv_manager.write_row('BESTXYZ', row)

    def _process_timea(self, line: str, timestamp: str, csv_manager: CSVWriterManager):
        row = self.parsers['TIMEA'].parse(timestamp, line)
        if row and self.frequency_filter.should_record('TIME'):
            csv_manager.write_row('TIME', row)

    def _process_psrdopa(self, line: str, timestamp: str, csv_manager: CSVWriterManager):
        row = self.parsers['PSRDOPA'].parse(timestamp, line)
        if row and self.frequency_filter.should_record('PSRDOP'):
            csv_manager.write_row('PSRDOP', row)

    def _process_hwmonitora(self, line: str, timestamp: str, csv_manager: CSVWriterManager):
        row = self.parsers['HWMONITORA'].parse(timestamp, line)
        if row and self.frequency_filter.should_record('HWMONITOR'):
            csv_manager.write_row('HWMONITOR', row)

    def _process_gpgsv(self, reader: LogReader, initial_lines: list,
                       timestamp: str, csv_manager: CSVWriterManager) -> int:
        lines = initial_lines.copy()

        row, consumed = self.parsers['GPGSV'].parse_multi(timestamp, lines)
        if row and self.frequency_filter.should_record('GPGSV'):
            csv_manager.write_row('GPGSV', row)

        return consumed


def parse_oem719_log(input_file: str, output_dir: str):
    parser = OEM719Parser(input_file, output_dir)
    parser.parse()
