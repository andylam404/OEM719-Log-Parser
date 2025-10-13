"""
Log file reader with offset and GPS lock detection.
"""

from typing import TextIO, Generator


class LogReader:
    """Reads OEM719 log files with offset and GPS lock detection."""

    def __init__(self, file_path: str, offset_bytes: int = 1000000):
        """
        Initialize log reader.

        Args:
            file_path: Path to log file
            offset_bytes: Byte offset to start reading from (default: 1MB)
        """
        self.file_path = file_path
        self.offset_bytes = offset_bytes
        self.file_handle = None

    def __enter__(self):
        """Open file for reading."""
        self.file_handle = open(self.file_path, 'r', encoding='utf-8', errors='ignore')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close file handle."""
        if self.file_handle:
            self.file_handle.close()

    def find_gps_lock(self, max_lines: int = 100) -> bool:
        """
        Check if GPS has acquired lock (FINESTEERING status).

        Args:
            max_lines: Maximum number of lines to check

        Returns:
            True if GPS lock found
        """
        start_pos = self.file_handle.tell()

        for _ in range(max_lines):
            line = self.file_handle.readline()
            if not line:
                break
            if 'FINESTEERING' in line:
                self.file_handle.seek(start_pos)
                return True

        self.file_handle.seek(start_pos)
        return False

    def seek_to_start_position(self) -> bool:
        """
        Seek to starting position (offset or GPS lock).

        Returns:
            True if GPS lock was found
        """
        # Seek to offset
        self.file_handle.seek(self.offset_bytes)

        # Read until line break to align with message boundaries
        self.file_handle.readline()

        # Check if we have GPS lock
        has_lock = self.find_gps_lock()

        return has_lock

    def read_lines(self) -> Generator[str, None, None]:
        """
        Generator that yields lines from the log file.

        Yields:
            Stripped lines from the log file
        """
        while True:
            line = self.file_handle.readline()
            if not line:
                break

            line = line.strip()
            if line:
                yield line
