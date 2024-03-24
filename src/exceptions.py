class ParserException(Exception):
    """An exception caused by the parsing logic."""
    pass


class EvaluationException(Exception):
    pass


class CircularDependenciesException(Exception):
    pass
