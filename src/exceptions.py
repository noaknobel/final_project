class ParserException(Exception):
    """An exception caused by the parsing logic."""
    pass


class CircularDependenciesException(Exception):
    """An exception caused by a cycle in a formula dependency graph."""
    pass


class FormulaEvaluationException(Exception):
    """A failure to evaluate a cell content."""
    pass


class BadNameException(FormulaEvaluationException):
    """A failure to evaluate a cell due to missing / invalid cell name."""
    pass


class BadValueException(FormulaEvaluationException):
    """A failure to evaluate a cell an error during the computation, e.g. division by zero."""
    pass
