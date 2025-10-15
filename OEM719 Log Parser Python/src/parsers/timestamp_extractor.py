import re
from datetime import datetime
from typing import Optional


class TimestampExtractor:
    def __init__(self):
        self.last_timestamp = None
        self.message_count = 0

    def extract_from_line(self, line: str) -> Optional[str]:
        match = re.search(r',(\d+),(\d+\.\d+),', line)
        if match:
            week = int(match.group(1))
            seconds = float(match.group(2))
            timestamp = self._format_gps_time(week, seconds)
            self.last_timestamp = timestamp
            self.message_count += 1
            return timestamp

        return self.last_timestamp

    def _format_gps_time(self, week: int, seconds: float) -> str:
        gps_epoch = datetime(1980, 1, 6)
        total_seconds = week * 7 * 24 * 3600 + seconds
        try:
            from datetime import timedelta
            dt = gps_epoch + timedelta(seconds=total_seconds)
            return dt.strftime("%m/%d/%Y %I:%M:%S.%f %p")[:-3]
        except:
            return datetime.now().strftime("%m/%d/%Y %I:%M:%S.%f %p")[:-3]

    def get_current_timestamp(self) -> str:
        now = datetime.now()
        return now.strftime("%m/%d/%Y %I:%M:%S.%f %p")[:-7] + now.strftime("%f")[:3] + now.strftime(" %p")
