import argparse

from dino.args import collect_serial_args
from dino.openscale_serial import OpenScaleReader
from dino.openscale_serial.openscale_reader import read_from_serial


def main():

    args = collect_serial_args(
        argparse.ArgumentParser(description="Print data from serial port")
    ).parse_args()

    reader = OpenScaleReader(print)
    read_from_serial(
        reader.handle_line, port=args.port, baud=args.baudrate, limit=args.limit
    )


if __name__ == "__main__":
    main()
