import re
from typing import List, Optional, Tuple


class MessageParser:
    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        raise NotImplementedError


class BestXYZParser(MessageParser):
    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        match = re.match(r'#BESTXYZA,([^;]+);(.+)\*', line)
        if not match:
            return None

        header_part = match.group(1)
        data_part = match.group(2)

        header_fields = [f.strip() for f in header_part.split(',')]
        data_fields = [f.strip() for f in data_part.split(',')]

        data_fields = [f.replace('""', '') for f in data_fields]

        row = [timestamp, '#BESTXYZA'] + header_fields[0:] + data_fields
        return row


class TimeAParser(MessageParser):
    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        match = re.match(r'#TIMEA,([^;]+);(.+)\*', line)
        if not match:
            return None

        header_part = match.group(1)
        data_part = match.group(2)

        header_fields = [f.strip() for f in header_part.split(',')]
        data_fields = [f.strip() for f in data_part.split(',')]

        row = [timestamp, '#TIMEA'] + header_fields[0:] + data_fields

        if len(row) > 12:
            try:
                offset_val = float(row[12])
                row[12] = f"{offset_val:.5E}"
            except (ValueError, IndexError):
                pass
        if len(row) > 13:
            try:
                offset_std = float(row[13])
                row[13] = f"{offset_std:.5E}"
            except (ValueError, IndexError):
                pass

        return row


class PSRDOPAParser(MessageParser):
    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        match = re.match(r'#PSRDOPA,([^;]+);(.+)\*', line)
        if not match:
            return None

        header_part = match.group(1)
        data_part = match.group(2)

        header_fields = [f.strip() for f in header_part.split(',')]
        data_fields = [f.strip() for f in data_part.split(',')]

        row = [timestamp, '#PSRDOPA'] + header_fields[0:] + data_fields[:6]
        return row


class HWMonitorAParser(MessageParser):
    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        match = re.match(r'#HWMONITORA,([^;]+);(.+)\*', line)
        if not match:
            return None

        header_part = match.group(1)
        data_part = match.group(2)

        header_fields = [f.strip() for f in header_part.split(',')]
        data_fields = [f.strip() for f in data_part.split(',')]

        readings = {}
        for i in range(1, len(data_fields), 2):
            if i + 1 < len(data_fields):
                value = data_fields[i]
                identifier = data_fields[i + 1]
                readings[identifier] = value

        row = [timestamp, '#HWMONITORA'] + header_fields[0:] + [
            readings.get('100', ''),
            readings.get('200', ''),
            readings.get('600', ''),
            readings.get('700', ''),
            readings.get('800', ''),
            readings.get('f00', ''),
            readings.get('1100', ''),
            readings.get('1500', ''),
            readings.get('1600', ''),
            '0', '0', '0', '0', '0', '0', '0', '0', '0'
        ]

        return row


class GPGSVParser(MessageParser):
    def parse_multi(self, timestamp: str, lines: List[str]) -> Tuple[Optional[List[str]], int]:
        satellite_data = []
        total_sats = 0
        lines_consumed = 0

        for line in lines:
            if not line.startswith('$GPGSV'):
                break
            lines_consumed += 1

            match = re.match(r'\$GPGSV,(\d+),(\d+),(\d+),(.+)\*', line)
            if not match:
                continue

            total_msgs = int(match.group(1))
            msg_num = int(match.group(2))
            total_sats = int(match.group(3))
            sat_info = match.group(4).split(',')

            satellite_data.extend(sat_info)

        if lines_consumed == 0:
            return None, 0

        max_sats = 100
        row = [timestamp, str(total_sats)]

        for i in range(max_sats * 4):
            if i < len(satellite_data) and satellite_data[i].strip():
                row.append(satellite_data[i].strip())
            else:
                row.append('#NV')

        return row, lines_consumed
