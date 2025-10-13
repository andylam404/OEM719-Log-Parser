"""
Message parsers for different OEM719 GPS message types.
Each parser is responsible for parsing a specific message format.
"""

import re
from typing import List, Optional, Tuple


class MessageParser:
    """Base class for message parsers."""

    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        """Parse a message line and return row data."""
        raise NotImplementedError


class BestXYZParser(MessageParser):
    """Parser for BESTXYZA messages."""

    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        """Parse BESTXYZA message."""
        match = re.match(r'#BESTXYZA,([^;]+);(.+)\*', line)
        if not match:
            return None

        header_part = match.group(1)
        data_part = match.group(2)

        header_fields = [f.strip() for f in header_part.split(',')]
        data_fields = [f.strip() for f in data_part.split(',')]

        # Remove quotes from empty string field
        data_fields = [f.replace('""', '') for f in data_fields]

        row = [timestamp, '#BESTXYZA'] + header_fields[1:] + data_fields
        return row


class TimeAParser(MessageParser):
    """Parser for TIMEA messages."""

    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        """Parse TIMEA message."""
        match = re.match(r'#TIMEA,([^;]+);(.+)\*', line)
        if not match:
            return None

        header_part = match.group(1)
        data_part = match.group(2)

        header_fields = [f.strip() for f in header_part.split(',')]
        data_fields = [f.strip() for f in data_part.split(',')]

        row = [timestamp, '#TIMEA'] + header_fields[1:] + data_fields

        # Convert the offset to scientific notation if needed
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
    """Parser for PSRDOPA messages."""

    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        """Parse PSRDOPA message."""
        match = re.match(r'#PSRDOPA,([^;]+);(.+)\*', line)
        if not match:
            return None

        header_part = match.group(1)
        data_part = match.group(2)

        header_fields = [f.strip() for f in header_part.split(',')]
        data_fields = [f.strip() for f in data_part.split(',')]

        row = [timestamp, '#PSRDOPA'] + header_fields[1:] + data_fields[:6]
        return row


class HWMonitorAParser(MessageParser):
    """Parser for HWMONITORA messages."""

    def parse(self, timestamp: str, line: str) -> Optional[List[str]]:
        """Parse HWMONITORA message."""
        match = re.match(r'#HWMONITORA,([^;]+);(.+)\*', line)
        if not match:
            return None

        header_part = match.group(1)
        data_part = match.group(2)

        header_fields = [f.strip() for f in header_part.split(',')]
        data_fields = [f.strip() for f in data_part.split(',')]

        # Parse hardware monitor data format: count, value1, id1, value2, id2, ...
        readings = {}
        for i in range(1, len(data_fields), 2):
            if i + 1 < len(data_fields):
                value = data_fields[i]
                identifier = data_fields[i + 1]
                readings[identifier] = value

        # Map to expected output format
        row = [timestamp, '#HWMONITORA'] + header_fields[1:] + [
            readings.get('100', ''),   # Temperature
            readings.get('200', ''),   # Antenna Current
            readings.get('600', ''),   # Digital Core 3V3 Voltage
            readings.get('700', ''),   # Antenna Voltage
            readings.get('800', ''),   # Digital 1V2 Core Voltage
            readings.get('f00', ''),   # Regulated Supply Voltage
            readings.get('1100', ''),  # 1V8
            readings.get('1500', ''),  # 5V Voltage
            readings.get('1600', ''),  # Secondary Temperature
            '0', '0', '0', '0', '0', '0', '0', '0', '0'  # Status flags (all 0)
        ]

        return row


class GPGSVParser(MessageParser):
    """Parser for GPGSV messages (can span multiple lines)."""

    def parse_multi(self, timestamp: str, lines: List[str]) -> Tuple[Optional[List[str]], int]:
        """
        Parse GPGSV message (can span multiple lines).
        Returns (row_data, num_lines_consumed)
        """
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

        # Create output row with #NV for missing values
        max_sats = 100  # Maximum satellites we support in the header
        row = [timestamp, str(total_sats)]

        # Add satellite data, pad with #NV
        for i in range(max_sats * 4):  # Each satellite has 4 fields
            if i < len(satellite_data) and satellite_data[i].strip():
                row.append(satellite_data[i].strip())
            else:
                row.append('#NV')

        return row, lines_consumed
