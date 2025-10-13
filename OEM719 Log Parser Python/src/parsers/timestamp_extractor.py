"""
Timestamp extraction and management for OEM719 log messages.
"""

import re
from datetime import datetime
from typing import Optional


class TimestampExtractor:
    """Extracts and manages timestamps from log messages."""

    def __init__(self):
        """Initialize timestamp extractor."""
        self.last_timestamp = None
        self.message_count = 0

    def extract_from_line(self, line: str) -> Optional[str]:
        """
        Extract timestamp from a log line if present.

        The OEM719 log doesn't have explicit timestamps on each line,
        but we can infer them from the message sequence and timing.

        Args:
            line: Log line to extract timestamp from

        Returns:
            Timestamp string or None
        """
        # Try to find time status and GPS time
        # Format in header: Week,Seconds
        match = re.search(r',(\d+),(\d+\.\d+),', line)
        if match:
            week = int(match.group(1))
            seconds = float(match.group(2))
            # Convert GPS time to readable format (simplified)
            timestamp = self._format_gps_time(week, seconds)
            self.last_timestamp = timestamp
            self.message_count += 1
            return timestamp

        # If no timestamp found, use the last known timestamp
        return self.last_timestamp

    def _format_gps_time(self, week: int, seconds: float) -> str:
        """
        Format GPS time to readable timestamp.

        This is a simplified version. In production, you'd convert GPS time
        to UTC properly considering GPS epoch (Jan 6, 1980).

        Args:
            week: GPS week number
            seconds: Seconds into the week

        Returns:
            Formatted timestamp string
        """
        # GPS epoch: January 6, 1980
        gps_epoch = datetime(1980, 1, 6)

        # Calculate days and remaining seconds
        total_seconds = week * 7 * 24 * 3600 + seconds

        # Create datetime (this is approximate)
        try:
            from datetime import timedelta
            dt = gps_epoch + timedelta(seconds=total_seconds)
            return dt.strftime("%m/%d/%Y %I:%M:%S.%f %p")[:-3]
        except:
            # Fallback to current time if calculation fails
            return datetime.now().strftime("%m/%d/%Y %I:%M:%S.%f %p")[:-3]

    def get_current_timestamp(self) -> str:
        """
        Get current timestamp or generate one if none available.

        Returns:
            Current timestamp string
        """
        if self.last_timestamp:
            return self.last_timestamp

        return datetime.now().strftime("%m/%d/%Y %I:%M:%S.%f %p")[:-3]
