class ParserException(Exception):
    """An exception caused by the parsing logic."""
    pass


class CircularDependenciesException(Exception):
    """An exception caused by a cycle in a formula dependency graph."""
    pass


class EvaluationException(Exception):
    """A failure to evaluate a cell content."""
    pass


class BadNameException(Exception):
    """A failure to evaluate a cell due to missing / invalid cell name."""
    pass
