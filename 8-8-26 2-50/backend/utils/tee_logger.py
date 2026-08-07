"""
tee_logger.py

Mirrors everything printed to the terminal into a timestamped log file,
without changing any existing print() calls in the agents.
"""

import sys
import os
from datetime import datetime


class TimestampedTee:
    def __init__(self, filepath: str, stream):
        self.stream = stream
        self.file = open(filepath, "a", encoding="utf-8")
        self._at_line_start = True

    def write(self, data: str):
        self.stream.write(data)
        for char in data:
            if self._at_line_start and char != "\n":
                ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
                self.file.write(ts)
                self._at_line_start = False
            self.file.write(char)
            if char == "\n":
                self._at_line_start = True
        self.file.flush()

    def flush(self):
        self.stream.flush()
        self.file.flush()


def start_logging(workflow_id: str) -> str:
    """Redirects stdout/stderr to also write into logs/<workflow_id>.log."""
    log_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "logs"
    )
    os.makedirs(log_dir, exist_ok=True)

    filepath = os.path.join(log_dir, f"{workflow_id}.log")

    sys.stdout = TimestampedTee(filepath, sys.stdout)
    sys.stderr = TimestampedTee(filepath, sys.stderr)

    return filepath