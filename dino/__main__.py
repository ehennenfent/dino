from functools import partial
from threading import Thread

from dino import (
    DinoStateMachine,
    Event,
    State,
    PatternMatcher,
    OpenScaleReader,
    Plotter,
)
from dino.buffer import Buffer
from dino.openscale_serial.__main__ import collect_args
from dino.openscale_serial.openscale_reader import (
    read_from_serial,
)
from dino.pattern_matching.patterns import eq_5p


def pass_to_plotter(plotter: Plotter, series_name: str, buffer: Buffer):
    plotter.get_differentiable_series(series_name).append(buffer.last_item)


def main():
    args = collect_args()

    # Create a matplotlib window to view the animated data
    plotter = Plotter()

    state_machine = DinoStateMachine()
    pattern_matcher = PatternMatcher()
    buffer = Buffer()

    pattern_matcher.register_pattern(
        "steady",
        (eq_5p, eq_5p, eq_5p, eq_5p),  # 5 samples within 5% of each other calibrates us
        partial(state_machine.receive_event, Event.STEADY),
    )

    state_machine.register_callback(
        State.UNCALIBRATED, State.STEADY, lambda: print("Calibrated!")
    )

    # Create a reader that's bound to the plotter
    reader = OpenScaleReader(buffer.append)
    buffer.register_callback(
        partial(
            Buffer.call_with_last_item,
            plotter.get_differentiable_series("Force").append,
        )
    )
    buffer.register_callback(
        partial(Buffer.call_with_underlying, pattern_matcher.match)
    )

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
