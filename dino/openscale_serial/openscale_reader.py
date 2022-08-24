import typing as t

from serial import Serial

DEFAULT_PORT = "COM4"
DEFAULT_BAUD = 115_200
SAMPLES_PER_SEC = 20


def read_from_serial(
    callback: t.Callable, port=DEFAULT_PORT, baud=DEFAULT_BAUD, limit=None
):
    """Read data from the openscale serial port"""

    def do_read():
        with Serial(port, baud, timeout=1) as ser:
            while True:
                yield ser.readline()

    for i, line in enumerate(do_read()):
        res = callback(line)
        if (limit is not None and i > limit) or (res is not None and not res):
            break


class OpenScaleReader:
    """Helper class to drop everything before `Readings:` and parse everything after"""

    def __init__(
        self,
        primary_callback: t.Callable = None,
    ):
        self.is_reading: bool = False
        self.should_read: bool = True
        self.callback: t.Callable = primary_callback

    def handle_line(self, line: bytes) -> bool:
        line = line.decode("utf-8").strip()

        # Sometimes we get empty lines
        if not line:
            return self.should_read

        # At some point we might want to do something with the metadata that gets printed before "Readings:" For now,
        # drop it.
        if not self.is_reading and line.startswith("Readings:"):
            self.is_reading = True
            return self.should_read

        if self.is_reading:
            # This probably needs better error handling in case we get malformed output. It's a microcontroller,
            # after all.
            ts, weight, _unit, _ = tuple(line.split(","))

            relevant = (int(ts), float(weight))

            if (res := self.callback(*relevant)) is not None:
                self.should_read = res

        return self.should_read

    def stop(self):
        self.should_read = False
