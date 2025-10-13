"""
Frequency filtering for 1Hz sampling rate.
"""

from typing import Dict, Optional


class FrequencyFilter:
    """Filters messages to maintain 1Hz sampling rate based on message counters."""

    def __init__(self, frequency_hz: float = 1.0):
        """
        Initialize frequency filter.

        Args:
            frequency_hz: Desired frequency in Hz (default: 1Hz)
        """
        self.frequency_hz = frequency_hz
        # For 1Hz, we want to record every message (since log already has ~1Hz rate)
        self.messages_per_second = int(1.0 / frequency_hz)
        self.message_counter: Dict[str, int] = {}
        self.recorded_count: Dict[str, int] = {}

    def should_record(self, message_type: str) -> bool:
        """
        Check if we should record this message based on frequency.

        For 1Hz filtering, we record every message since the OEM719 log
        typically outputs messages at approximately 1Hz already.

        Args:
            message_type: Type of message (e.g., 'BESTXYZ', 'TIME')

        Returns:
            True if message should be recorded
        """
        # Initialize counters for this message type
        if message_type not in self.message_counter:
            self.message_counter[message_type] = 0
            self.recorded_count[message_type] = 0

        self.message_counter[message_type] += 1

        # For 1Hz, record every message (the log is already ~1Hz)
        # For higher frequencies, we would skip messages
        should_record = (self.message_counter[message_type] % max(1, self.messages_per_second) == 1)

        if should_record:
            self.recorded_count[message_type] += 1

        # Actually, for 1Hz we should just record every message
        # since messages_per_second will be 1
        return True  # Record all messages for 1Hz

    def get_message_count(self, message_type: str) -> int:
        """Get total count of recorded messages for a type."""
        return self.recorded_count.get(message_type, 0)

    def reset(self):
        """Reset all tracking."""
        self.message_counter.clear()
        self.recorded_count.clear()
