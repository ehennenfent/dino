import typing as t

from dino.openscale_serial.openscale_reader import SAMPLES_PER_SEC
from .types import State, Event


class DinoStateMachine:
    def __init__(self):
        self.current_state = State.UNCALIBRATED
        self.allowed_transitions = {
            State.UNCALIBRATED: {State.UNCALIBRATED, State.STEADY},
            State.STEADY: {State.STEADY, State.DUCKING, State.JUMPING},
            State.JUMPING: {State.JUMPING, State.STEADY},
            State.DUCKING: {State.DUCKING, State.STEADY, State.JUMPING},
        }
        self.transition_callbacks = {}
        self.time_in_state = 0

    def register_callback(
        self, from_state: State, to_state: State, callback: t.Callable
    ):
        self.transition_callbacks.setdefault(from_state, dict())[to_state] = callback

    def receive_event(self, event: Event):
        new_state = self.current_state

        if self.current_state == State.UNCALIBRATED:
            if event == event.VELOCITY_STEADY:
                new_state = State.STEADY
        elif self.current_state == State.STEADY:
            if event in (Event.VELOCITY_POSITIVE_SMALL, Event.VELOCITY_POSITIVE_LARGE):
                new_state = State.JUMPING
            if event == Event.VELOCITY_NEGATIVE:
                new_state = State.DUCKING
        elif self.current_state == State.JUMPING:
            if event == Event.VELOCITY_STEADY:
                new_state = State.STEADY
            # Revert to steady after time passes
            if self.time_in_state >= SAMPLES_PER_SEC // 5:
                new_state = State.STEADY
        elif self.current_state == State.DUCKING:
            if event == Event.VELOCITY_POSITIVE_SMALL:
                new_state = State.STEADY
            if event == Event.VELOCITY_POSITIVE_LARGE:
                new_state = State.JUMPING

        self.transition(new_state)

    def tick(self, *_args):
        self.time_in_state += 1

    def transition(self, new_state: State):
        if new_state in self.allowed_transitions.get(self.current_state, set()):
            if new_state != self.current_state:
                print(self.current_state, "-->", new_state)
                self.time_in_state = 0

            maybe_callback = self.transition_callbacks.get(self.current_state, {}).get(
                new_state, None
            )
            self.current_state = new_state
            if maybe_callback is not None:
                maybe_callback()
        else:
            raise RuntimeError(
                f"Transition from {self.current_state} to {new_state} is not allowed"
            )
