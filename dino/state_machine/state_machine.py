import typing as t
from enum import Enum, auto


class State(Enum):
    UNCALIBRATED = auto()
    STEADY = auto()
    JUMP_START = auto()
    JUMPING = auto()
    JUMP_END = auto()

    # Currently unused
    DUCK_START = auto()
    DUCKING = auto()
    DUCK_END = auto()


class Event(Enum):
    SPIKE_START_POSITIVE = auto()
    SPIKE_END_POSITIVE = auto()
    SPIKE_PEAK_POSITIVE = auto()
    SPIKE_START_NEGATIVE = auto()
    SPIKE_END_NEGATIVE = auto()
    SPIKE_PEAK_NEGATIVE = auto()
    STEADY = auto()


class DinoStateMachine:
    def __init__(self):
        self.current_state = State.UNCALIBRATED
        self.allowed_transitions = {
            State.UNCALIBRATED: {State.STEADY},
            State.STEADY: {},
            State.JUMP_START: {},
            State.JUMPING: {},
            State.JUMP_END: {},
        }
        self.transition_callbacks = {}

    def register_callback(
        self, from_state: State, to_state: State, callback: t.Callable
    ):
        self.transition_callbacks.setdefault(from_state, dict())[to_state] = callback

    def receive_event(self, event: Event):
        new_state = self.current_state

        if self.current_state == State.UNCALIBRATED:
            pass
        elif self.current_state == State.STEADY:
            if event == Event.SPIKE_START_NEGATIVE:
                new_state = State.JUMP_START
        elif self.current_state == State.JUMP_START:
            pass
        elif self.current_state == State.JUMPING:
            pass
        elif self.current_state == State.JUMP_END:
            pass

        self.transition(new_state)

    def transition(self, new_state: State):
        if new_state in self.allowed_transitions.get(self.current_state, set()):
            self.current_state = new_state
            maybe_callback = self.transition_callbacks.get(self.current_state, {}).get(
                new_state, None
            )
            if maybe_callback is not None:
                maybe_callback()
        else:
            raise RuntimeError(
                f"Transition from {self.current_state} to {new_state} is not allowed"
            )
