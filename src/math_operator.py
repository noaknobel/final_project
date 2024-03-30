import math
from enum import Enum, auto


class Associativity(Enum):
    """
    Defines the associativity of a mathematical operator, determining the direction
    an expression is evaluated when operators have the same precedence.
    """
    LTR = auto()  # Left to Right
    RTL = auto()  # Right to Left


class MathOperator:
    """
    Represents a mathematical operator. This is a base class for defining operators
    with a symbol, precedence, and associativity. It provides a structure for operator
    calculation but does not implement it.

    Attributes:
        symbol (str): The symbol representing the operator.
        precedence (int): Determines the order of operations.
        associativity (Associativity): Direction of operation evaluation.

    Methods:
        calculate: Should be implemented by subclasses to perform the operation.
    """
    def __init__(self, symbol: str, precedence: int, associativity: Associativity):
        self.symbol = symbol
        self.precedence = precedence
        self.associativity = associativity

    def calculate(self, *args):
        """
        Placeholder for the calculation method. Subclasses should implement this method.
        """
        raise NotImplementedError("This method should be implemented by specific operator subclasses")


class UnaryOperator(MathOperator):
    """
    Represents a unary mathematical operator, operating on a single operand. Subclasses
    must implement the calculation logic specific to the unary operation.
    Inherits from MathOperator.
   """
    def __init__(self, symbol: str, precedence: int = 3, associativity: Associativity = Associativity.RTL):
        super().__init__(symbol, precedence, associativity)

    def calculate(self, operand):
        """
        Placeholder for unary operation calculation. To be implemented by subclasses.
        """
        raise NotImplementedError


class BinaryOperator(MathOperator):
    """
    Represents a binary mathematical operator, operating on two operands. Subclasses
    must implement the calculation logic specific to the binary operation.

    Inherits from MathOperator.
    """
    def __init__(self, symbol: str, precedence: int = 1, associativity: Associativity = Associativity.LTR):
        super().__init__(symbol, precedence, associativity)

    def calculate(self, left_operand, right_operand):
        """
        Placeholder for binary operation calculation. To be implemented by subclasses.
        """
        raise NotImplementedError


class RangeOperator(MathOperator):
    """
    Represents a range operator, operating on a list of operands. These operators perform
    operations over a range of values. Subclasses must implement the specific range operation.

    Inherits from MathOperator.
    """
    def __init__(self, symbol: str, precedence: int = 3, associativity: Associativity = Associativity.RTL):
        super().__init__(symbol, precedence, associativity)

    def calculate(self, operands: list[float]):
        """
        Placeholder for range operation calculation. To be implemented by subclasses.
        """
        raise NotImplementedError


# Implementing specific operators

class Plus(BinaryOperator):
    def __init__(self):
        super().__init__("+", 1)

    def calculate(self, left_operand: float, right_operand: float) -> float:
        return left_operand + right_operand


class Minus(BinaryOperator):
    def __init__(self):
        super().__init__("-", 1)

    def calculate(self, left_operand, right_operand):
        return left_operand - right_operand


class Times(BinaryOperator):
    def __init__(self):
        super().__init__("*", 2)

    def calculate(self, left_operand, right_operand):
        return left_operand * right_operand


class Divide(BinaryOperator):
    def __init__(self):
        super().__init__("/", 2)

    def calculate(self, left_operand, right_operand):
        return left_operand / right_operand


class Power(BinaryOperator):
    def __init__(self):
        super().__init__("^", 4, Associativity.RTL)

    def calculate(self, left_operand, right_operand):
        return math.pow(left_operand, right_operand)


class Negate(UnaryOperator):
    def __init__(self):
        super().__init__("-", 3)

    def calculate(self, operand):
        return -operand


class Sin(UnaryOperator):
    def __init__(self):
        super().__init__("sin", 3)

    def calculate(self, operand: float) -> float:
        return math.sin(operand)


class Max(RangeOperator):
    def __init__(self):
        super().__init__("max")

    def calculate(self, operands: list[float]):
        return max(operands)


class Min(RangeOperator):
    def __init__(self):
        super().__init__("min")

    def calculate(self, operands: list[float]):
        return min(operands)


class Sum(RangeOperator):
    def __init__(self):
        super().__init__("sum")

    def calculate(self, operands: list[float]) -> float:
        return sum(operands)


class Average(RangeOperator):
    def __init__(self):
        super().__init__("average")

    def calculate(self, operands: list[float]):
        return sum(operands)/len(operands)
