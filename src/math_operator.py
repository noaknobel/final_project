import math
from enum import Enum, auto


class Associativity(Enum):
    LTR = auto()  # Left to Right
    RTL = auto()  # Right to Left


class MathOperator:
    def __init__(self, symbol: str, precedence: int, associativity: Associativity):
        self.symbol = symbol
        self.precedence = precedence
        self.associativity = associativity

    def calculate(self, *args):
        raise NotImplementedError("This method should be implemented by specific operator subclasses")


class UnaryOperator(MathOperator):
    def __init__(self, symbol: str, precedence: int = 3, associativity: Associativity = Associativity.RTL):
        super().__init__(symbol, precedence, associativity)

    def calculate(self, operand):
        """This method should be implemented by specific unary operator subclasses"""
        raise NotImplementedError


class BinaryOperator(MathOperator):
    def __init__(self, symbol: str, precedence: int = 1, associativity: Associativity = Associativity.LTR):
        super().__init__(symbol, precedence, associativity)

    def calculate(self, left_operand, right_operand):
        """This method should be implemented by specific binary operator subclasses"""
        raise NotImplementedError


class RangeOperator(MathOperator):
    def __init__(self, symbol: str, precedence: int = 3, associativity: Associativity = Associativity.RTL):
        super().__init__(symbol, precedence, associativity)

    def calculate(self, operands: list[float]):
        """This method should be implemented by specific unary operator subclasses"""
        raise NotImplementedError


# Implementing specific operators

class Plus(BinaryOperator):
    def __init__(self):
        super().__init__("+", 1)

    def calculate(self, left_operand, right_operand):
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

    def calculate(self, operand):
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

    def calculate(self, operands: list[float]):
        return sum(operands)


class Average(RangeOperator):
    def __init__(self):
        super().__init__("average")

    def calculate(self, operands: list[float]):
        return sum(operands)/len(operands)
