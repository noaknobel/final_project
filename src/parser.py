import re
from typing import List, Union

from expression_operator import Operator, OperatorType, Associativity
from node import Node


# TODO - change to my own exception classes
class InvalidExpressionException(Exception):
    """The expression is not valid. Some operators or operands are missing."""
    pass


class InvalidParenthesesException(Exception):
    """The parenthesis are not balanced in the expression."""
    pass


class ExpressionParser:
    """Algebraic expression parser."""
    LOCATION_PATTERN = re.compile(r'^[A-Z]+[0-9]+$')

    def __init__(self, operators: List[Operator]) -> None:
        self.operators = operators

    def __is_operator(self, token):
        """Checks whether the given token equals a symbol of a valid operator."""
        return any(op.symbol == token for op in self.operators)

    def __is_operand(self, string: str) -> bool:
        """Checks whether the given string is a valid operand."""
        return self.__is_number(string) or self.__is_location(string)

    @classmethod
    def __is_location(cls, string: str) -> bool:
        """
        Checks whether a string is in the format of a valid location in the sheet,
        which is a column string of capital letters, followed by a row number.
        """
        return bool(cls.LOCATION_PATTERN.match(string))

    @staticmethod
    def __is_number(var: str) -> bool:
        """
        Checks whether a string can be parsed as a float number.
        If it starts with a sign (+ or -), or is wrapped with spaces,
        return false (should be considered as multiple tokens).
        """
        # Remove edge cases of float conversion.
        if len(var.strip()) != len(var) or var.startswith("+") or var.startswith("-"):
            return False
        # Try to convert the string to a float. If succeeds - the string can be parsed as a float number.
        try:
            float(var)
            return True
        except ValueError:
            return False

    @staticmethod
    def __is_open_bracket(char: str) -> bool:
        """Checks whether a string is an opening bracket."""
        return char == "(" or char == "[" or char == "{"

    @staticmethod
    def __is_close_bracket(char: str) -> bool:
        """Checks whether a string is a closing bracket."""
        return char == ")" or char == "]" or char == "}"

    def __is_bracket(self, char: str) -> bool:
        """Checks whether a string is a bracket."""
        return self.__is_close_bracket(char) or self.__is_open_bracket(char)

    def __is_valid_token(self, token: str) -> bool:
        return self.__is_bracket(token) or token.isspace() or self.__is_operand(token) or self.__is_operator(token)

    def __find_next_matching_token(self, expression: str, start_index: int) -> str:
        """
        A helper method that searches for a valid token that starts at the given start index in the expression.
        It continues until the end of the string and returns the longest valid token that starts at that index in case
        there are multiple ones. If there is none - return an empty string.
        """
        current_checked_substring = ""
        longest_valid_token = ""
        while start_index < len(expression):
            current_checked_substring += expression[start_index]  # the char in the expression at position idx.
            if self.__is_valid_token(current_checked_substring):
                longest_valid_token = current_checked_substring
            start_index += 1
        return longest_valid_token

    def tokenize(self, expression: str) -> List[str]:
        """
        Splits the expression into valid tokens.
        :raises InvalidExpressionException: If there is an invalid token in the expression.
        """
        index = 0
        tokens = []
        while index < len(expression):
            token = self.__find_next_matching_token(expression, index)
            if not token:
                raise InvalidExpressionException("Expression is not valid.")
            index += len(token)
            tokens.append(token)
        return tokens

    @staticmethod
    def __are_parentheses_pairs(open_bracket: str, close_bracket: str) -> bool:
        """Returns whether an open bracket matches a closing bracket."""
        return any([(open_bracket == "{" and close_bracket == "}"),
                    (open_bracket == "(" and close_bracket == ")"),
                    (open_bracket == "[" and close_bracket == "]")])

    @staticmethod
    def does_have_higher_precedence(operator1: Operator, operator2: Operator) -> bool:
        # TODO
        return (operator2.associativity == Associativity.LTR and operator2.precedence <= operator1.precedence) or (
                operator2.associativity == Associativity.RTL and operator2.precedence < operator1.precedence)

    def __generate_postfix(self, tokens: List[str], tokens_postfix: List[Union[Operator, str]]) -> None:
        """
        Gets a list of valid tokens and reorders them as a math equation in a postfix order.
        This method uses an operator stack to handle operators and parentheses, ensuring that the expression obeys
        mathematical rules and that parentheses are properly balanced.
        It appends all postfix items to the given tokens_postfix input parameter.
        Raises an exception if the expression does not obey math expression rules.
        """
        # If the expression is empty, raise an exception.
        if not tokens:
            raise InvalidExpressionException("Expression is not valid.")

        operators_stack: list[Union[Operator, str]] = []  # Stores Operator instances, and string parentheses.
        is_previous_character_operand = False
        tokens = [token for token in tokens if not token.isspace()]  # Skip white-space tokens
        for token in tokens:
            if self.__is_open_bracket(token):
                if is_previous_character_operand:  # Prevents "(operand(" without operator in between
                    raise InvalidExpressionException("An open bracket cannot directly follow an operand.")
                operators_stack.append(token)
                is_previous_character_operand = False

            elif self.__is_close_bracket(token):
                # Pop from the stack until an open bracket is found
                while operators_stack and not self.__is_open_bracket(operators_stack[-1]):
                    tokens_postfix.append(operators_stack.pop())
                if not operators_stack:
                    raise InvalidParenthesesException("Mismatched parentheses in expression.")
                open_bracket = operators_stack.pop()  # Pop the open bracket
                if not self.__are_parentheses_pairs(open_bracket, token):
                    raise InvalidParenthesesException(
                        f"Mismatched parentheses in expression: {open_bracket} and {token}")
                is_previous_character_operand = True  # A closed parenthesis can act as an operand

            elif self.__is_operator(token):
                # Find the matching operator
                matching_operators = [op for op in self.operators if op.symbol == token]
                operator = next((op for op in matching_operators if (
                    op.type == OperatorType.BINARY if is_previous_character_operand else op.type == OperatorType.UNARY
                )), None)

                if not operator:
                    raise InvalidExpressionException("Invalid operator in expression.")

                # Pop operators with higher or equal precedence
                while operators_stack and isinstance(operators_stack[-1], Operator) and \
                        self.does_have_higher_precedence(operators_stack[-1], operator):
                    tokens_postfix.append(operators_stack.pop())

                operators_stack.append(operator)
                is_previous_character_operand = False

            elif self.__is_operand(token):
                if is_previous_character_operand:
                    raise InvalidExpressionException("Cannot have two operands in a row.")
                tokens_postfix.append(token)
                is_previous_character_operand = True
            else:
                raise InvalidExpressionException(f"Invalid token in expression: {token}")

        # At the end of the expression, pop all remaining operators from the stack
        while operators_stack:
            if self.__is_open_bracket(operators_stack[-1]):
                raise InvalidParenthesesException("Mismatched parentheses in expression.")
            tokens_postfix.append(operators_stack.pop())

        # Ensure the expression ends with an operand
        if not is_previous_character_operand:
            raise InvalidExpressionException("The expression must end with an operand.")

    def __postfix(self, expression: str) -> List[Union[str, Operator]]:
        """Return the postfix form for the expression."""
        tokens = self.tokenize(expression)
        postfix = []
        self.__generate_postfix(tokens, postfix)
        return postfix

    def syntax_tree(self, expression: str) -> Node:
        """Return the expression syntax tree."""
        postfix: List[Union[str, Operator]] = self.__postfix(expression)
        stack = []
        i = 0
        while i < len(postfix):
            node = Node(postfix[i])
            if isinstance(postfix[i], Operator):
                node = Node(postfix[i].symbol)
                if postfix[i].type == OperatorType.UNARY:
                    if len(stack) < 1:
                        raise InvalidExpressionException("expression is not valid.")
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
    operators = [Operator(symbol='+'), Operator(symbol='-'),
                 Operator(symbol='*', precedence=2), Operator(symbol='/', precedence=2),
                 Operator(symbol='-', operator_type=OperatorType.UNARY, precedence=3, associativity=Associativity.RTL),
                 Operator(symbol='sin', operator_type=OperatorType.UNARY, precedence=3,
                          associativity=Associativity.RTL),
                 Operator(symbol='^', precedence=4, associativity=Associativity.RTL)]

    parser = ExpressionParser(operators)
    x = parser.syntax_tree('{-sin(-33) * (X2^3)} + A11')
    print(x)
    x = parser.syntax_tree('((1-2))')
    print(x)
    x = parser.syntax_tree('-sin1/3')
    print(x)
    x = parser.syntax_tree('({1 + 4 + 4 + 4} * [(1 + 5)+1]) + 1')
    print(x)
    x = parser.syntax_tree('1^2^3')
    print(x)
