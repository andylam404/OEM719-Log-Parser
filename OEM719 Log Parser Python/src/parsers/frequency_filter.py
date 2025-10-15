import time
from typing import Dict


class FrequencyFilter:
    def __init__(self, frequency_hz: float = 5.0):
        self.frequency_hz = frequency_hz
        self.sample_interval = 1.0 / frequency_hz
        self.last_sample_time = None
        self.recorded_count: Dict[str, int] = {}

    def wait_for_next_sample(self):
        current_time = time.time()

        if self.last_sample_time is None:
            self.last_sample_time = current_time
            return

        elapsed = current_time - self.last_sample_time
        time_to_wait = self.sample_interval - elapsed

        if time_to_wait > 0:
            time.sleep(time_to_wait)

        self.last_sample_time = time.time()

    def should_record(self, message_type: str) -> bool:
        if message_type not in self.recorded_count:
            self.recorded_count[message_type] = 0

        self.recorded_count[message_type] += 1
        return True

    def get_message_count(self, message_type: str) -> int:
        return self.recorded_count.get(message_type, 0)

    def reset(self):
        self.recorded_count.clear()
        self.last_sample_time = None
