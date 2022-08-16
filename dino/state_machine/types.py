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
