from typing import List, Set, Tuple, Union

from expression_operator import Operator, OperatorType, Traversal, Associativity
from node import Node


class InvalidExpressionException(Exception):
    """The expression is not valid. Some operators or operands are missing."""
    pass


class InvalidParenthesesException(Exception):
    """The parenthesis are not balanced in the expression."""
    pass


class ExpressionParser:
    """Algebraic expression parser."""

    def __init__(self, operators: List[Operator]) -> None:
        self.operators = operators

    def __str__(self) -> str:
        return str(self.operators)

    def __repr__(self) -> str:
        return f"ExpressionParser({self.operators.__repr__()})"

    def is_operator(self, token):
        return any(op.symbol == token for op in self.operators)

    @staticmethod
    def does_have_higher_precedence(operator1: Operator, operator2: Operator) -> bool:
        return (operator2.associativity == Associativity.LTR and operator2.precedence <= operator1.precedence) or (
                operator2.associativity == Associativity.RTL and operator2.precedence < operator1.precedence)

    def is_operand(self, c: str) -> bool:
        return self._is_constant(c) or self._is_variable(c)

    @staticmethod
    def _is_variable(c: str) -> bool:
        return c.isalpha() and len(c) == 1

    @staticmethod
    def _is_constant(c: str) -> bool:
        if len(c.strip()) != len(c) or c[0] == '+' or c[0] == '-' or c is None:
            return False
        try:
            float(c)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_open_bracket(c: str) -> bool:
        return c == "(" or c == "[" or c == "{"

    @staticmethod
    def is_close_bracket(c: str) -> bool:
        return c == ")" or c == "]" or c == "}"

    def _is_bracket(self, c: str) -> bool:
        return self.is_close_bracket(c) or self.is_open_bracket(c)

    @staticmethod
    def __are_pairs(bracket1: str, bracket2: str) -> bool:
        """Return True if the two brackets has the same type."""
        if bracket2 == "}" and bracket1 == "{":
            return True
        elif bracket2 == ")" and bracket1 == "(":
            return True
        elif bracket2 == "]" and bracket1 == "[":
            return True
        return False

    def __is_valid_token(self, token: str) -> bool:
        return self._is_bracket(token) or self.is_operand(token) or token.isspace() or self.is_operator(token)

    def _find_next_matching_token(self, expression: str, start_idx: int) -> Tuple[str, int]:
        token = ''
        accepted_lexeme = ''
        longest_idx = start_idx
        while start_idx < len(expression):
            token += expression[start_idx]
            if self.__is_valid_token(token):
                accepted_lexeme = token
                longest_idx = start_idx
            start_idx += 1
        return (accepted_lexeme, longest_idx)

    def tokenize(self, expression: str) -> List[str]:
        """Split the expression into tokens"""
        idx = 0
        tokens = []
        while idx < len(expression):
            token, next_idx = self._find_next_matching_token(expression, idx)
            if not token:
                raise InvalidExpressionException(
                    "expression is not valid.")
            idx = next_idx + 1
            tokens.append(token)
        return tokens

    def __parse(self, tokens: List[str], tokens_postfix: List[str]) -> None:
        """validates expression tokens and constructs postfix form from given tokens."""
        if not tokens:
            raise InvalidExpressionException(
                "expression is not valid.")
        sz = len(tokens)
        operators_stack: list[tuple[str, Operator]] = []
        is_previous_character_operand = False
        i = 0
        while i < sz:
            if self.is_open_bracket(tokens[i]):
                if is_previous_character_operand:
                    raise InvalidExpressionException(
                        "expression is not valid.")
                open_brackets_count = 0
                idx = i
                # find its close bracket.
                while open_brackets_count != 1 or not self.is_close_bracket(tokens[idx]):
                    if self.is_open_bracket(tokens[idx]):
                        open_brackets_count += 1
                    elif self.is_close_bracket(tokens[idx]):
                        open_brackets_count -= 1
                    idx += 1
                    if idx >= sz:
                        raise InvalidParenthesesException(
                            "expression's parenthesis are not balanced.")
                if not self.__are_pairs(tokens[i], tokens[idx]):
                    raise InvalidParenthesesException(
                        "expression's parenthesis are not balanced.")
                self.__parse(tokens[i + 1: idx], tokens_postfix)

                i = idx
                is_previous_character_operand = True

            elif self.is_close_bracket(tokens[i]):
                raise InvalidParenthesesException(
                    "expression's parenthesis are not balanced.")

            elif tokens[i].isspace():
                i += 1
                continue

            elif self.is_operator(tokens[i]):
                unary_rule = binary_rule = None
                is_valid = False
                for rule in (op for op in self.operators if op.symbol == tokens[i]):
                    if rule.type == OperatorType.UNARY:
                        unary_rule = rule
                    if rule.type == OperatorType.BINARY:
                        binary_rule = rule
                if unary_rule:
                    if (unary_rule.position == Traversal.POSTFIX and is_previous_character_operand) or (
                            unary_rule.position == Traversal.PREFIX and not is_previous_character_operand):
                        is_valid = True
                        binary_rule = None
                if binary_rule:
                    if is_previous_character_operand:
                        is_valid = True
                        unary_rule = None
                    is_previous_character_operand = False
                if not is_valid:
                    raise InvalidExpressionException(
                        "expression is not valid.")
                while operators_stack and self.does_have_higher_precedence(operators_stack[-1][1],
                                                                           unary_rule if unary_rule else binary_rule):
                    tokens_postfix.append(operators_stack[-1][1])
                    operators_stack.pop()
                operators_stack.append(
                    (tokens[i], unary_rule if unary_rule else binary_rule))
                print("OP stack:", operators_stack)
            elif self.is_operand(tokens[i]):
                if is_previous_character_operand:
                    raise InvalidExpressionException(
                        "expression is not valid.")
                is_previous_character_operand = True
                tokens_postfix.append(tokens[i])

            else:
                raise InvalidExpressionException(
                    "expression is not valid.")
            i += 1
        if not is_previous_character_operand:
            raise InvalidExpressionException(
                "expression is not valid.")
        while operators_stack:
            tokens_postfix.append(operators_stack[-1][1])
            operators_stack.pop()

    def postfix(self, expression: str, include_operators_rules: bool = False) -> List[Union[str, Operator]]:
        """Return the postfix form for the expression."""
        if not isinstance(expression, str):
            raise TypeError(
                f"expression has to be str. {expression} is {type(expression)}, not str.")

        tokens = self.tokenize(expression)
        postfix = []
        self.__parse(tokens, postfix)
        if not include_operators_rules:
            postfix = [c.symbol if isinstance(c, Operator) else c for c in postfix]
        return postfix

    def syntax_tree(self, expression: str) -> Node:
        """Return the expression syntax tree."""
        postfix: List[Union[str, Operator]] = self.postfix(expression, include_operators_rules=True)
        stack = []
        i = 0
        while i < len(postfix):
            node = Node(postfix[i])
            if isinstance(postfix[i], Operator):
                node = Node(postfix[i].symbol)
                if postfix[i].type == OperatorType.UNARY:
                    if postfix[i].position == Traversal.POSTFIX:
                        if len(stack) < 1:
                            raise InvalidExpressionException(
                                "expression is not valid.")
                        node.left = stack.pop()
                    if postfix[i].position == Traversal.PREFIX:
                        if len(stack) < 1:
                            raise InvalidExpressionException(
                                "expression is not valid.")
                        node.right = stack.pop()
                if postfix[i].type == OperatorType.BINARY:
                    if len(stack) < 2:
                        raise InvalidExpressionException(
                            "expression is not valid.")
                    node.right = stack.pop()
                    node.left = stack.pop()
            stack.append(node)
            i += 1
        return stack.pop()


if __name__ == '__main__':
    operators = [Operator(symbol='+'), Operator(symbol='-'), Operator(symbol='*', precedence=2),
                 Operator(symbol='-', operator_type=OperatorType.UNARY, precedence=3, associativity=Associativity.RTL,
                          position=Traversal.PREFIX),
                 Operator(symbol='^', precedence=4),
                 Operator(symbol='sin', operator_type=OperatorType.UNARY, precedence=3, associativity=Associativity.RTL,
                          position=Traversal.PREFIX)]

    parser = ExpressionParser(operators)
    x = parser.syntax_tree('(-3) * (x^3)')
    print(x)
    x = parser.syntax_tree('((1 + 4 + 4 + 4) * (1 + 5)) + 1')
    print(x)
