"""
OEM719 GPS Log Parser

This module parses OEM719 GPS receiver log files and extracts different message types
into separate CSV files. It supports 1Hz sampling rate and 30-second duration limits.
"""

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
    """Main parser for OEM719 GPS log files."""

    def __init__(self, input_file: str, output_dir: str,
                 offset_bytes: int = 1000000,
                 max_duration_seconds: int = 30,
                 frequency_hz: float = 1.0):
        """
        Initialize OEM719 parser.

        Args:
            input_file: Path to input log file
            output_dir: Directory to save output CSV files
            offset_bytes: Byte offset to start reading (default: 1MB)
            max_duration_seconds: Maximum parsing duration (default: 30s)
            frequency_hz: Sampling frequency (default: 1Hz)
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.offset_bytes = offset_bytes

        # Initialize components
        self.timestamp_extractor = TimestampExtractor()
        self.frequency_filter = FrequencyFilter(frequency_hz=frequency_hz)
        self.duration_limiter = DurationLimiter(max_duration_seconds=max_duration_seconds)

        # Initialize message parsers
        self.parsers = {
            'BESTXYZA': BestXYZParser(),
            'TIMEA': TimeAParser(),
            'PSRDOPA': PSRDOPAParser(),
            'HWMONITORA': HWMonitorAParser(),
            'GPGSV': GPGSVParser()
        }

    def parse(self):
        """Parse the OEM719 log file and generate CSV outputs."""
        print(f"Starting OEM719 log parser...")
        print(f"Input file: {self.input_file}")
        print(f"Output directory: {self.output_dir}")

        with LogReader(self.input_file, self.offset_bytes) as reader:
            # Seek to start position
            print("Seeking to start position (1MB offset or GPS lock)...")
            has_lock = reader.seek_to_start_position()

            if has_lock:
                print("Found GPS lock, starting parsing...")
            else:
                print("Warning: No GPS lock found after 1MB offset, continuing anyway...")

            # Initialize CSV writers
            with CSVWriterManager(self.output_dir) as csv_manager:
                # Parse messages
                line_count = 0
                line_buffer = []

                for line in reader.read_lines():
                    line_count += 1

                    # Extract timestamp from line
                    timestamp = self.timestamp_extractor.extract_from_line(line)
                    if not timestamp:
                        timestamp = self.timestamp_extractor.get_current_timestamp()

                    # Start duration timer on first valid message
                    if not self.duration_limiter.is_started():
                        self.duration_limiter.start()

                    # Process message based on type
                    if '#BESTXYZA' in line:
                        self._process_bestxyz(line, timestamp, csv_manager)

                    elif '#TIMEA' in line:
                        self._process_timea(line, timestamp, csv_manager)

                    elif '#PSRDOPA' in line:
                        self._process_psrdopa(line, timestamp, csv_manager)

                    elif '#HWMONITORA' in line:
                        self._process_hwmonitora(line, timestamp, csv_manager)

                    elif '$GPGSV' in line:
                        # Collect multi-line GPGSV messages
                        line_buffer = [line]
                        consumed = self._process_gpgsv(reader, line_buffer, timestamp, csv_manager)

                    # Write to RAW data log
                    csv_manager.write_row('RAW', [timestamp, f'"{line}\n"'])

                    # Check duration limit
                    if self.duration_limiter.has_expired():
                        print(f"\nReached {self.duration_limiter.get_elapsed_seconds():.1f}s duration limit")
                        break

                    # Progress indicator
                    if line_count % 1000 == 0:
                        elapsed = self.duration_limiter.get_elapsed_seconds()
                        print(f"Processed {line_count} lines... (elapsed: {elapsed:.1f}s)")

                # Print results
                print("\nParsing complete!")
                print(f"Total lines processed: {line_count}")
                print(f"\nMessages written:")
                for msg_type, count in csv_manager.get_all_counts().items():
                    print(f"  {msg_type}: {count}")
                print(f"\nOutput files created in: {self.output_dir}")

    def _process_bestxyz(self, line: str, timestamp: str, csv_manager: CSVWriterManager):
        """Process BESTXYZA message."""
        row = self.parsers['BESTXYZA'].parse(timestamp, line)
        if row and self.frequency_filter.should_record('BESTXYZ'):
            csv_manager.write_row('BESTXYZ', row)

    def _process_timea(self, line: str, timestamp: str, csv_manager: CSVWriterManager):
        """Process TIMEA message."""
        row = self.parsers['TIMEA'].parse(timestamp, line)
        if row and self.frequency_filter.should_record('TIME'):
            csv_manager.write_row('TIME', row)

    def _process_psrdopa(self, line: str, timestamp: str, csv_manager: CSVWriterManager):
        """Process PSRDOPA message."""
        row = self.parsers['PSRDOPA'].parse(timestamp, line)
        if row and self.frequency_filter.should_record('PSRDOP'):
            csv_manager.write_row('PSRDOP', row)

    def _process_hwmonitora(self, line: str, timestamp: str, csv_manager: CSVWriterManager):
        """Process HWMONITORA message."""
        row = self.parsers['HWMONITORA'].parse(timestamp, line)
        if row and self.frequency_filter.should_record('HWMONITOR'):
            csv_manager.write_row('HWMONITOR', row)

    def _process_gpgsv(self, reader: LogReader, initial_lines: list,
                       timestamp: str, csv_manager: CSVWriterManager) -> int:
        """Process GPGSV message (can span multiple lines)."""
        # Peek ahead to collect all GPGSV lines
        lines = initial_lines.copy()

        # Note: In production, you'd need to implement peek-ahead in LogReader
        # For now, we'll just process the initial line

        row, consumed = self.parsers['GPGSV'].parse_multi(timestamp, lines)
        if row and self.frequency_filter.should_record('GPGSV'):
            csv_manager.write_row('GPGSV', row)

        return consumed


def parse_oem719_log(input_file: str, output_dir: str):
    """
    Convenience function to parse OEM719 GPS log file.

    Args:
        input_file: Path to the input log file
        output_dir: Directory to save output CSV files
    """
    parser = OEM719Parser(input_file, output_dir)
    parser.parse()
