from enum import Enum, auto


class State(Enum):
    UNCALIBRATED = auto()
    STEADY = auto()
    JUMPING = auto()
    DUCKING = auto()


class Event(Enum):
    VELOCITY_POSITIVE_SMALL = auto()
    VELOCITY_POSITIVE_LARGE = auto()
    VELOCITY_NEGATIVE = auto()
    VELOCITY_STEADY = auto()
