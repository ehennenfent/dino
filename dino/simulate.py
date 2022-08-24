import typing as t
from time import sleep


class Simulator:
    def __init__(self, file: t.TextIO, callback: t.Callable):
        self.file = file
        self.callback = callback
        self.last_ts = 0
        self.should_read = True

    def simulate(self):
        for line in self.file:
            if not self.should_read:
                break
            ts, magnitude = self.parse_line(line)
            sleep((ts - self.last_ts) / 1000)
            self.callback(ts, magnitude)
            self.last_ts = ts

    @staticmethod
    def parse_line(line: str) -> t.Tuple[int, float]:
        ts, magnitude = eval(line.strip())
        return ts, magnitude

    def stop(self):
        self.should_read = False
        self.file.close()
