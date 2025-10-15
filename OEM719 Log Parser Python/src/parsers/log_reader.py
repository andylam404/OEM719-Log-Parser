from typing import TextIO, Generator


class LogReader:
    def __init__(self, file_path: str, offset_bytes: int = 1000000):
        self.file_path = file_path
        self.offset_bytes = offset_bytes
        self.file_handle = None

    def __enter__(self):
        self.file_handle = open(self.file_path, 'r', encoding='utf-8', errors='ignore')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_handle:
            self.file_handle.close()

    def find_gps_lock(self, max_lines: int = 100) -> bool:
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
        self.file_handle.seek(self.offset_bytes)

        self.file_handle.readline()

        has_lock = self.find_gps_lock()

        return has_lock

    def read_lines(self) -> Generator[str, None, None]:
        while True:
            line = self.file_handle.readline()
            if not line:
                break

            line = line.strip()
            if line:
                yield line
