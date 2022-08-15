from functools import partial
from threading import Thread

from dino.plotter.plot import Plotter
from dino.plotter.read_serial import OpenScaleReader, read_from_serial, collect_args
from dino.state_machine.pattern_matcher import PatternMatcher
from dino.state_machine.patterns import eq_5p
from dino.state_machine.state_machine import DinoStateMachine, State


def main():
    args = collect_args()

    # Create a matplotlib window to view the animated data
    plotter = Plotter()

    state_machine = DinoStateMachine()
    pattern_matcher = PatternMatcher()

    pattern_matcher.register_pattern(
        "steady",
        (eq_5p, eq_5p, eq_5p, eq_5p),  # 5 samples within 5% of each other calibrates us
        partial(state_machine.receive_event, State.STEADY),
    )

    state_machine.register_callback(
        State.UNCALIBRATED, State.STEADY, lambda: print("Calibrated!")
    )

    def pass_to_plotter(*my_args):
        plotter.get_differentiable_series("FOrce").append(my_args)
        # pattern_matcher.match(plotter.)

    # Create a reader that's bound to the plotter
    reader = OpenScaleReader(pass_to_plotter)

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
