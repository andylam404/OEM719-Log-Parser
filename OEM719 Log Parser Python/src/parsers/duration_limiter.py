"""
Duration limiter for controlling parsing duration.
"""

from datetime import datetime, timedelta
from typing import Optional


class DurationLimiter:
    """Limits parsing duration to a specified time period."""

    def __init__(self, max_duration_seconds: int = 30):
        """
        Initialize duration limiter.

        Args:
            max_duration_seconds: Maximum duration in seconds (default: 30)
        """
        self.max_duration = timedelta(seconds=max_duration_seconds)
        self.start_time: Optional[datetime] = None

    def start(self):
        """Start the duration timer."""
        self.start_time = datetime.now()

    def is_started(self) -> bool:
        """Check if timer has been started."""
        return self.start_time is not None

    def has_expired(self) -> bool:
        """
        Check if the duration limit has been exceeded.

        Returns:
            True if duration has expired
        """
        if not self.start_time:
            return False

        elapsed = datetime.now() - self.start_time
        return elapsed >= self.max_duration

    def get_elapsed_seconds(self) -> float:
        """
        Get elapsed time in seconds.

        Returns:
            Elapsed seconds or 0 if not started
        """
        if not self.start_time:
            return 0.0

        return (datetime.now() - self.start_time).total_seconds()

    def get_remaining_seconds(self) -> float:
        """
        Get remaining time in seconds.

        Returns:
            Remaining seconds or max duration if not started
        """
        if not self.start_time:
            return self.max_duration.total_seconds()

        remaining = self.max_duration - (datetime.now() - self.start_time)
        return max(0.0, remaining.total_seconds())
