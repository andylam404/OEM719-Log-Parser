from datetime import datetime, timedelta
from typing import Optional


class DurationLimiter:
    def __init__(self, max_duration_seconds: int = 30):
        self.max_duration = timedelta(seconds=max_duration_seconds)
        self.start_time: Optional[datetime] = None

    def start(self):
        self.start_time = datetime.now()

    def is_started(self) -> bool:
        return self.start_time is not None

    def has_expired(self) -> bool:
        if not self.start_time:
            return False

        elapsed = datetime.now() - self.start_time
        return elapsed >= self.max_duration

    def get_elapsed_seconds(self) -> float:
        if not self.start_time:
            return 0.0

        return (datetime.now() - self.start_time).total_seconds()

    def get_remaining_seconds(self) -> float:
        if not self.start_time:
            return self.max_duration.total_seconds()

        remaining = self.max_duration - (datetime.now() - self.start_time)
        return max(0.0, remaining.total_seconds())
