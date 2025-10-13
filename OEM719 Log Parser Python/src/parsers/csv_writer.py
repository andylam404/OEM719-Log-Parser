"""
CSV writer for OEM719 log data.
"""

import os
import csv
from typing import Dict, List
from .csv_headers import HEADERS


class CSVWriterManager:
    """Manages multiple CSV writers for different message types."""

    def __init__(self, output_dir: str):
        """
        Initialize CSV writer manager.

        Args:
            output_dir: Directory to save CSV files
        """
        self.output_dir = output_dir
        self.csv_files: Dict[str, object] = {}
        self.csv_writers: Dict[str, csv.writer] = {}
        self.messages_written: Dict[str, int] = {}

        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def __enter__(self):
        """Initialize all CSV files."""
        for msg_type, headers in HEADERS.items():
            filename = self._get_filename(msg_type)
            filepath = os.path.join(self.output_dir, filename)

            # Open file with UTF-8 BOM to match reference output
            self.csv_files[msg_type] = open(filepath, 'w', newline='', encoding='utf-8-sig')
            self.csv_writers[msg_type] = csv.writer(self.csv_files[msg_type])
            self.csv_writers[msg_type].writerow(headers)
            self.messages_written[msg_type] = 0

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close all CSV files."""
        for f in self.csv_files.values():
            f.close()

    def _get_filename(self, msg_type: str) -> str:
        """Get filename for message type."""
        if msg_type == 'BESTXYZ':
            return 'BESTXYZ.csv'
        elif msg_type == 'RAW':
            return 'GPS RAW DATA.csv'
        else:
            return f'GPS {msg_type}.csv'

    def write_row(self, msg_type: str, row: List[str]) -> bool:
        """
        Write a row to the appropriate CSV file.

        Args:
            msg_type: Message type (e.g., 'BESTXYZ', 'TIME')
            row: Row data to write

        Returns:
            True if write was successful
        """
        if msg_type not in self.csv_writers:
            return False

        self.csv_writers[msg_type].writerow(row)
        self.messages_written[msg_type] = self.messages_written.get(msg_type, 0) + 1
        return True

    def get_message_count(self, msg_type: str) -> int:
        """Get count of messages written for a type."""
        return self.messages_written.get(msg_type, 0)

    def get_all_counts(self) -> Dict[str, int]:
        """Get all message counts."""
        return self.messages_written.copy()
