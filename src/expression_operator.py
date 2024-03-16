from enum import Enum, auto


class OperatorType(Enum):
    UNARY = auto()
    BINARY = auto()


class Traversal(Enum):
    PREFIX = auto()
    INFIX = auto()
    POSTFIX = auto()


class Associativity(Enum):
    LTR = auto()
    RTL = auto()


class Operator:
    def __init__(self, symbol: str, precedence: int = 1, operator_type: OperatorType = OperatorType.BINARY,
                 associativity: Associativity = Associativity.LTR, position: Traversal = Traversal.INFIX) -> None:
        """
        :param symbol: represents the operator.
        :param operator_type: represents the operator type. It accepts two values unary or binary.
        :param precedence: represents the operator precedence.
        :param associativity: represents the operator associativity.
        :param position: string represents the operator position.
        """
        self.symbol = symbol
        self.type = operator_type
        self.precedence = precedence
        self.associativity = associativity
        self.position = position

    def __str__(self) -> str:
        return f"symbol: {self.symbol}\ntype: {self.type}\nprecedence: {self.precedence}\nassociativity: {self.associativity}\nposition: {self.position}"

    def __repr__(self) -> str:
        return f"Operator(symbol='{self.symbol}', type={self.type}, precedence={self.precedence}, associativity='{self.associativity}')"
