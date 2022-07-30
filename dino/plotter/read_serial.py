import argparse
import typing as t
from collections import deque

from serial import Serial

DEFAULT_PORT = "COM4"
DEFAULT_BAUD = 115_200
SAMPLES_PER_SEC = 1


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

    def __init__(self, callback: t.Callable = None, maxlen=SAMPLES_PER_SEC * 60 * 20):
        self.is_reading: bool = False
        self.should_read: bool = True
        self.buffer = deque(maxlen=maxlen)
        self.callback: t.Callable = callback

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
            ts, weight, _unit, _temp_onboard, _temp_remote, _ = tuple(line.split(","))

            relevant = (int(ts), float(weight))
            self.buffer.append(relevant)

            if (res := self.callback(*relevant)) is not None:
                self.should_read = res

        return self.should_read

    def stop(self):
        self.should_read = False


def collect_args():
    parser = argparse.ArgumentParser(description="Print data from serial port")
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        action="store",
        default=DEFAULT_PORT,
        help="COM/Serial port to read from",
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        type=int,
        action="store",
        default=DEFAULT_BAUD,
        help="Read with the given baud rate",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        action="store",
        default=None,
        help="Stop reading after this many lines",
    )

    return parser.parse_args()


def main():

    args = collect_args()

    reader = OpenScaleReader(print)
    read_from_serial(
        reader.handle_line, port=args.port, baud=args.baudrate, limit=args.limit
    )


if __name__ == "__main__":
    main()
