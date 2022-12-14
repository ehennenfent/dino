import argparse

from dino.openscale_serial.openscale_reader import DEFAULT_PORT, DEFAULT_BAUD


def collect_serial_args(parser):
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

    return parser


def collect_simulate_args(parser):
    parser.add_argument(
        "simulation_data_file",
        type=str,
        action="store",
        help="File from which to read dumped simulation data",
    )
    return parser


def collect_plot_args(parser):
    parser.add_argument(
        "-d",
        "--n_derivatives",
        type=int,
        action="store",
        default=0,
        help="Number of derivatives to show on the plot",
    )

    parser.add_argument(
        "-i",
        "--n_integrals",
        type=int,
        action="store",
        default=1,
        help="Number of integrals to show on the plot",
    )

    return parser


def collect_args():
    parser = argparse.ArgumentParser(description="Run the openscale tooling")
    operations = parser.add_subparsers(title="commands", dest="command", required=True)

    simulate_parser = operations.add_parser(
        "simulate", help="Read scale data from a dump file"
    )
    plot_parser = operations.add_parser(
        "plot", help="Plot live readings from the openscale"
    )

    _plot_parser = collect_serial_args(collect_plot_args(plot_parser))
    _simulate_parser = collect_simulate_args(collect_plot_args(simulate_parser))

    return parser.parse_args()
