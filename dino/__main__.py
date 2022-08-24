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
from dino.pattern_matching.patterns import eq_1p, mag_rel, abs_rel
from dino.physics import PhysicsSolver
from dino.simulate import Simulator

SHORT_SAMPLES = 3
POS_LARGE_THRESH = 20
POS_SMALL_THRESH = 7
NEG_THRESH = -3
STABLE_THRESH = 1


def main():
    args = collect_args()

    # Create a matplotlib window to view the animated data
    plotter = Plotter(n_derivates=0)

    # Make a state machine to keep track of what part of a jump we're in
    state_machine = DinoStateMachine()

    # Make a pattern matcher to help us recognize trends in the data
    force_matcher = PatternMatcher()
    velocity_matcher = PatternMatcher()

    # Add a buffer to store the last several samples
    buffer = Buffer()

    physics = PhysicsSolver(buffer)

    # Create some patterns
    force_matcher.register_pattern(
        "steady_1s",
        (eq_1p,) * SAMPLES_PER_SEC,  # 20 samples within 1% of each other
        physics.calibrate_steady_state,
    )

    velocity_matcher.register_pattern(
        "steady_velocity",
        (mag_rel(operator.lt, STABLE_THRESH),)
        * (SAMPLES_PER_SEC // 5),  # 20 samples within 1% of each other
        partial(state_machine.receive_event, Event.VELOCITY_STEADY),
    )

    velocity_matcher.register_pattern(
        "negative",
        (abs_rel(operator.lt, NEG_THRESH),)
        * SHORT_SAMPLES,  # 20 samples within 1% of each other
        partial(state_machine.receive_event, Event.VELOCITY_NEGATIVE),
    )

    velocity_matcher.register_pattern(
        "positive_small",
        (abs_rel(operator.gt, POS_SMALL_THRESH),)
        * SHORT_SAMPLES,  # 20 samples within 1% of each other
        partial(state_machine.receive_event, Event.VELOCITY_POSITIVE_SMALL),
    )

    velocity_matcher.register_pattern(
        "positive_large",
        (abs_rel(operator.gt, POS_LARGE_THRESH),)
        * SHORT_SAMPLES,  # 20 samples within 1% of each other
        partial(state_machine.receive_event, Event.VELOCITY_POSITIVE_LARGE),
    )

    def draw_vline(color):
        current_ts, _ = buffer.last_item
        plotter.draw_vertical_line(current_ts, color)

    state_machine.register_callback(
        State.STEADY, State.JUMPING, partial(draw_vline, "green")
    )
    state_machine.register_callback(
        State.DUCKING, State.JUMPING, partial(draw_vline, "green")
    )
    state_machine.register_callback(
        State.STEADY, State.DUCKING, partial(draw_vline, "red")
    )

    def pass_tared_to_plotter(last_item):
        ts, y = last_item
        plotter.get_differentiable_series("Force").append(
            (ts, physics.correct_for_tare(y))
        )

    # Plot the data as it comes in
    buffer.register_callback(
        partial(
            Buffer.call_with_last_item,
            pass_tared_to_plotter,
        )
    )

    # Attempt to pattern match on incoming data
    buffer.register_callback(partial(Buffer.call_with_underlying, force_matcher.match))

    physics.velocity.register_callback(
        partial(Buffer.call_with_underlying, velocity_matcher.match)
    )

    physics.velocity.register_callback(
        partial(
            Buffer.call_with_last_item,
            plotter.get_differentiable_series("Velocity").append,
        )
    )

    # physics.position.register_callback(
    #     partial(
    #         Buffer.call_with_last_item,
    #         plotter.get_differentiable_series("Position").append,
    #     )
    # )

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


if __name__ == "__main__":
    main()
