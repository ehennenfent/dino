from collections import deque
import typing as t
from dino.openscale_serial.openscale_reader import SAMPLES_PER_SEC

BUFFER_MINUTES = 1


class Buffer:
    def __init__(self, maxlen=SAMPLES_PER_SEC * 60 * BUFFER_MINUTES):
        self.buffer = deque(maxlen=maxlen)
        self.callbacks = []

    def append(self, *next_item):
        self.buffer.append(next_item)

        for cb in self.callbacks:
            cb(self)

    @property
    def last_item(self):
        return self.buffer[-1]

    @staticmethod
    def call_with_last_item(callback: t.Callable, b: "Buffer"):
        return callback(b.last_item)

    @staticmethod
    def call_with_underlying(callback: t.Callable, b: "Buffer"):
        return callback(b.buffer)

    def register_callback(self, cb: t.Callable):
        self.callbacks.append(cb)

    def dump(self, file_like: t.TextIO):
        for line in self.buffer:
            file_like.write(repr(line) + "\n")

    def is_empty(self):
        return len(self.buffer) == 0

    def clear(self):
        self.buffer.clear()

    def __getitem__(self, item):
        return self.buffer[item]

    def __iter__(self):
        return iter(self.buffer)
