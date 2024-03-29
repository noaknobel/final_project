from enum import Enum, auto


class FailureReason(Enum):
    DEPENDENCIES_CYCLE = auto()
    COULD_NOT_PARSE = auto()
    UNEXPECTED_EXCEPTION = auto()
    EVALUATION_FAILURE = auto()
    BAD_NAME_REFERENCE = auto()
    ZERO_DIVISION = auto()