import operator
from functools import partial
from threading import Thread

from dino import (
    DinoStateMachine,
    PatternMatcher,
    OpenScaleReader,
    Plotter,
    State,
    Event,
)
from dino.args import collect_args
from dino.buffer import Buffer
from dino.openscale_serial.openscale_reader import (
    read_from_serial,
    SAMPLES_PER_SEC,
)
from dino.pattern_matching.patterns import (
    mag_rel,
    tare,
    peak_up,
    peak_down,
)
from dino.physics import PhysicsSolver
from dino.simulate import Simulator
from dino.socket_rpc import SocketSender

SHORT_SAMPLES = 3
POS_LARGE_THRESH = 20
POS_SMALL_THRESH = 7
NEG_THRESH = -3
STABLE_THRESH = 1


def main():
    args = collect_args()

    # Create a matplotlib window to view the animated data
    plotter = Plotter(n_derivates=args.n_derivatives)
    # Make a pattern matcher to help us recognize trends in the data
    force_matcher = PatternMatcher()
    velocity_matcher = PatternMatcher()

    socket_rpc = SocketSender()

    # Add a buffer to store the last several samples
    buffer = Buffer()

    # Add a simple state machine to tare the data and calculate user weight/velocity/position
    physics = PhysicsSolver(buffer)

    # Create some patterns
    register_default_patterns(force_matcher, physics, velocity_matcher,         lambda color: plotter.draw_vertical_line(buffer.last_item[0], color),
        socket_rpc)

    # Plot the data as it comes in
    def pass_tared_to_plotter(last_item):
        ts, y = last_item
        plotter.get_differentiable_series("Force").append(
            (ts, physics.correct_for_tare(y))
        )

    buffer.register_callback(
        partial(
            Buffer.call_with_last_item,
            pass_tared_to_plotter,
        )
    )

    if args.n_integrals >= 1:
        physics.velocity.register_callback(
            partial(
                Buffer.call_with_last_item,
                plotter.get_differentiable_series("Velocity").append,
            )
        )

    if args.n_integrals >= 2:
        physics.position.register_callback(
            partial(
                Buffer.call_with_last_item,
                plotter.get_differentiable_series("Position").append,
            )
        )

    # Attempt to pattern match on incoming data
    buffer.register_callback(partial(Buffer.call_with_underlying, force_matcher.match))

    physics.velocity.register_callback(
        partial(Buffer.call_with_underlying, velocity_matcher.match)
    )

    # Either ingest or simulate the data
    if args.command == "plot":
        # Create a reader that feeds data to the buffer
        reader = OpenScaleReader(buffer.append)

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

    elif args.command == "simulate":
        # Read a trace of weights from a file
        reader = Simulator(open(args.simulation_data_file, "r"), buffer.append)

        runner = Thread(
            target=reader.simulate,
            daemon=True,
        )
    else:
        raise RuntimeError(f"Unknown command: {args.command}")

    runner.start()

    # Show the graph. This will block until the X button is clicked
    plotter.animate()
    print("Stopped animation")

    # Kill the thread reading the data
    reader.stop()


def register_default_patterns(force_matcher, physics, velocity_matcher, draw_vline, socket_rpc):
    def on_jump():
        draw_vline("green")
        socket_rpc.send(b"j")

    def on_steady():
        # draw_vline("orange")
        socket_rpc.send(b"s")

    force_matcher.register_pattern(
        "steady_1s",
        (tare,)
        * SAMPLES_PER_SEC,  # 20 samples either close to each other or very small
        physics.calibrate_steady_state,
    )
    velocity_matcher.register_pattern(
        "steady_velocity",
        (mag_rel(operator.lt, STABLE_THRESH),) * (SAMPLES_PER_SEC // 5),
        on_steady,
    )
    velocity_matcher.register_pattern(
        "positive_large",
        (peak_up, peak_up),
        on_jump,
    )


if __name__ == "__main__":
    main()
