import argparse

from dino.openscale_serial import OpenScaleReader
from dino.openscale_serial.openscale_reader import (
    DEFAULT_PORT,
    DEFAULT_BAUD,
    read_from_serial,
)


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
