from enum import Enum, auto


class FailureReason(Enum):
    """
    Enumerates various reasons for failures within the system.

    - DEPENDENCIES_CYCLE: Indicates a cycle in dependencies, which prevents evaluation.
    - COULD_NOT_PARSE: Indicates the input could not be parsed successfully.
    - UNEXPECTED_EXCEPTION: Indicates an unexpected exception occurred during processing.
    - EVALUATION_FAILURE: Indicates a failure occurred during the evaluation of an expression.
    - BAD_NAME_REFERENCE: Indicates a reference to a non-existent or invalid name.
    - ZERO_DIVISION: Indicates an attempt to divide by zero was detected.
    """
    DEPENDENCIES_CYCLE = auto()
    COULD_NOT_PARSE = auto()
    UNEXPECTED_EXCEPTION = auto()
    EVALUATION_FAILURE = auto()
    BAD_NAME_REFERENCE = auto()
    ZERO_DIVISION = auto()