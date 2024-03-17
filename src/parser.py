import re
from typing import List, Union

from expression_operator import Operator, OperatorType, Traversal, Associativity
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
        The method works recursively and does the same operation for each sub expression (in parentheses).
        The method appends all postfix items to the given tokens_postfix input param.
        Raises an exception if the expression does not obey math expression rules.
        """
        # If the expression (or an inner expression in brackets) is empty - raise an exception.
        if not tokens:
            raise InvalidExpressionException("Expression is not valid.")
        number_of_tokens = len(tokens)
        operators_stack: list[Operator] = []
        is_previous_character_operand = False
        i = 0
        while i < number_of_tokens:

            # If there is a sub-expression in brackets - find the end of the brackets and recursively add it.
            if self.__is_open_bracket(tokens[i]):
                if is_previous_character_operand:
                    raise InvalidExpressionException("Open bracket must can't come directly after an operand.")
                open_brackets_count = 0
                idx = i
                # find its close bracket.
                while not (open_brackets_count == 1 and self.__is_close_bracket(tokens[idx])):
                    if self.__is_open_bracket(tokens[idx]):
                        open_brackets_count += 1
                    elif self.__is_close_bracket(tokens[idx]):
                        open_brackets_count -= 1
                    idx += 1
                    if idx >= number_of_tokens:
                        raise InvalidParenthesesException(
                            "expression's parenthesis are not balancved.")
                if not self.__are_parentheses_pairs(tokens[i], tokens[idx]):
                    raise InvalidParenthesesException(
                        "expression's parenthesis are not balanced.")
                self.__generate_postfix(tokens[i + 1: idx], tokens_postfix)

                i = idx
                is_previous_character_operand = True

            # If there was a close bracket not handled by the previous block -
            # it doesn't have a matching openner and its an error.
            elif self.__is_close_bracket(tokens[i]):
                raise InvalidParenthesesException("Expression's parenthesis are not balanced.")

            # Skip white-space tokens.
            elif tokens[i].isspace():
                i += 1
                continue

            elif self.__is_operator(tokens[i]):

                # Find matching operator from the list that matches the operator symbol.
                # If there are both unary and binary operators with that same symbol - choose the correct one.
                unary_rule = binary_rule = None
                is_valid = False
                for matching_operator in (op for op in self.operators if op.symbol == tokens[i]):
                    if matching_operator.type == OperatorType.UNARY:
                        unary_rule = matching_operator
                    if matching_operator.type == OperatorType.BINARY:
                        binary_rule = matching_operator
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

                # If none of them are valid - raise an exception.
                if not is_valid:
                    raise InvalidExpressionException("expression is not valid.")
                current_operator = unary_rule if unary_rule else binary_rule

                # Pop from the operators stack all operators that have higher precedence than the current operator,
                # and move them to the postfix array before handling the current operator,
                # so their order in the tree later on will be according to the correct computation order
                while operators_stack and self.does_have_higher_precedence(operators_stack[-1], current_operator):
                    top = operators_stack.pop()
                    tokens_postfix.append(top)
                operators_stack.append(current_operator)


            elif self.__is_operand(tokens[i]):
                # Can't have 2 operands one after another.
                if is_previous_character_operand:
                    raise InvalidExpressionException("expression is not valid.")
                is_previous_character_operand = True
                # If the token is an operand, simply add it to the postfix list.
                tokens_postfix.append(tokens[i])
            else:
                # Unexpected token - wasn't true for any of the if-else cases above.
                raise InvalidExpressionException("expression is not valid.")
            # Move to the next token in the loop of the expression.
            i += 1

        # Must finish the expression (or any sub-expression) with an operand.
        if not is_previous_character_operand:
            raise InvalidExpressionException("expression is not valid.")
        # Any operators left in the stack of the current expression - pop and move to the postfix list. todo - why? when? example?
        while operators_stack:
            top = operators_stack.pop()
            tokens_postfix.append(top)

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
    operators = [Operator(symbol='+'), Operator(symbol='/', precedence=2), Operator(symbol='-'),
                 Operator(symbol='*', precedence=2),
                 Operator(symbol='-', operator_type=OperatorType.UNARY, precedence=3, associativity=Associativity.RTL,
                          position=Traversal.PREFIX),
                 Operator(symbol='^', precedence=4),
                 Operator(symbol='sin', operator_type=OperatorType.UNARY, precedence=3, associativity=Associativity.RTL,
                          position=Traversal.PREFIX)]

    parser = ExpressionParser(operators)
    x = parser.syntax_tree('{-sin(-33) * (X2^3)} + A11')
    print(x)
    x = parser.syntax_tree('((1-2))')
    x = parser.syntax_tree('-sin3')
    print(x)
    x = parser.syntax_tree('((1 + 4 + 4 + 4) * (1 + 5)) + 1')
    print(x)
