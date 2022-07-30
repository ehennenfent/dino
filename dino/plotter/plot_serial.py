from functools import partial
from threading import Thread

from dino.plotter.plot import Plotter
from dino.plotter.read_serial import OpenScaleReader, read_from_serial, collect_args


def pass_to_plotter(plotter: Plotter, series_name: str, *args):
    plotter.get_series(series_name).append(args)


def main():
    args = collect_args()

    # Create a matplotlib window to view the animated data
    plotter = Plotter()

    # Create a reader that's bound to the plotter
    reader = OpenScaleReader(partial(pass_to_plotter, plotter, "Force"))

    # Run the openscale data collection in the background so it can ingest data as fast as possible
    runner = Thread(
        target=partial(
            read_from_serial,
            reader.handle_line,
            port=args.port,
            baud=args.baudrate,
            limit=args.limit,
        ),
        daemon=True,
    )
    runner.start()

    # Show the graph. This will block until the X button is clicked
    plotter.animate()

    # Kill the thread reading the data
    reader.stop()


if __name__ == "__main__":
    main()
