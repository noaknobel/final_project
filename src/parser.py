import re
from typing import Callable, Optional
from typing import List, Union

from operator import Operator, OperatorType, Associativity
from node import Node


class ParserException(Exception):
    """An exception caused by the parsing logic."""
    pass


class ExpressionParser:
    """Algebraic expression parser."""
    LOCATION_PATTERN = re.compile(r'^[A-Z]+[0-9]+$')

    def __init__(self, operators: List[Operator]) -> None:
        """
        Initializes the ExpressionParser with a list of operators.
        :param operators: A list of Operator objects that are valid in the expressions this parser will parse.
        """
        self.operators = operators

    def __is_operator(self, token):
        """
        Checks whether the given token equals a symbol of a valid operator.
        :param token: The string to check.
        :return: True if the token is an operator, False otherwise.
        """
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
        """
        Checks if a given string is a valid token in the context of the parser.
        A valid token is either a bracket, a whitespace, an operand, or an operator.
        :param token: The string to check.
        :return: True if the token is valid, False otherwise.
        """
        return self.__is_bracket(token) or token.isspace() or self.__is_operand(token) or self.__is_operator(token)

    def __find_next_matching_token(self, expression: str, start_index: int) -> str:
        """
        Finds the next valid token in the expression starting from the given index.
        :param expression: The expression being parsed.
        :param start_index: The index from where to start the search.
        :return: The longest valid token starting from the start_index. Returns an empty string if no valid token is found.
        """
        current_checked_substring = ""
        longest_valid_token = ""
        while start_index < len(expression):
            current_checked_substring += expression[start_index]  # the char in the expression at position idx.
            if self.__is_valid_token(current_checked_substring):
                longest_valid_token = current_checked_substring
            start_index += 1
        return longest_valid_token

    def __tokenize(self, expression: str) -> List[str]:
        """
        Converts the expression into a list of valid tokens.
        :param expression: The expression to tokenize.
        :return: A list of strings where each string is a valid token in the expression.
        :raises ParserException: If an invalid token is found in the expression.
        """
        index = 0
        tokens = []
        while index < len(expression):
            token = self.__find_next_matching_token(expression, index)
            if not token:
                raise ParserException(f"Could not find a valid token at index {index} of the expression.")
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
    def __does_have_higher_precedence(operator1: Operator, operator2: Operator) -> bool:
        """
        Determines if the second (current) operator has higher precedence than the first (previous) operator.
        This is dependent on the operator's associativity and precedence.
        If the second operator is left-to-right associative and its precedence is less than or equal to that of the first,
        or if the second operator is right-to-left associative and its precedence is less than that of the first,
        then the second operator is considered to have higher precedence.

        :param operator1: The first operator (previously on the stack).
        :param operator2: The second operator (currently being considered).
        :return: True if the second operator has higher precedence, False otherwise.
        """
        return (operator2.associativity == Associativity.LTR and operator2.precedence <= operator1.precedence) or (
                operator2.associativity == Associativity.RTL and operator2.precedence < operator1.precedence)

    def __postfix(self, tokens: List[str]) -> List[Union[Operator, str]]:
        """
        Converts a list of tokens representing an algebraic expression into its postfix form.
        This method handles operator precedence, associativity, and parentheses.
        It ensures that operators with higher precedence are placed before operators with lower precedence in the output
         list. Parentheses are handled to enforce the proper ordering and grouping of operations.
        :param tokens: A list of strings representing the tokens of an algebraic expression.
        :return: A list containing the tokens of the expression arranged in postfix notation.
        :raises ParserException: If the expression contains syntax errors such as unbalanced parentheses,
                                 two operands in a row without an operator, or an open bracket directly following an
                                  operand. It also checks if the expression ends with an operand.
        """
        if not tokens:
            raise ParserException("List of tokens is empty.")
        tokens_postfix: List[Union[Operator, str]] = []
        operators_stack: list[Union[Operator, str]] = []  # Stores Operator instances, and parentheses strings.
        is_previous_character_operand = False
        tokens = [token for token in tokens if not token.isspace()]

        for token in tokens:
            is_previous_character_operand = self.__process_token_postfix(token, operators_stack, tokens_postfix,
                                                                         is_previous_character_operand)

        while operators_stack:
            tokens_postfix.append(operators_stack.pop())

        if not is_previous_character_operand:
            raise ParserException("The expression must end with an operand.")
        return tokens_postfix

    from typing import List, Union

    def __process_token_postfix(self, token: str, operators_stack: List[str],
                                tokens_postfix: List[Union[str, Operator]],
                                is_previous_character_operand: bool) -> bool:
        """
        Processes a single token in the postfix logic.
        :param token: The current token from the expression.
        :param operators_stack: A stack (implemented as a list) holding operators and parentheses during conversion.
        :param tokens_postfix: The list accumulating the postfix representation tokens.
        :param is_previous_character_operand: Flag indicating if the preceding token in the sequence was an operand.
        :return: Returns True if the processed token is an operand, otherwise False.
        :raises ParserException: Whether the token's arrangement breaks rules.
        """
        if self.__is_open_bracket(token):
            if is_previous_character_operand:
                raise ParserException("An open bracket cannot directly follow an operand.")
            operators_stack.append(token)
            return False
        if self.__is_close_bracket(token):
            self.__handle_close_bracket(operators_stack, tokens_postfix)
            return True
        if self.__is_operator(token):
            operator_type = OperatorType.BINARY if is_previous_character_operand else OperatorType.UNARY
            operator = self.__find_operator(token, operator_type)
            if operator is None:
                raise ParserException("Invalid operator in expression.")
            self.__handle_operator(operator, operators_stack, tokens_postfix)
            return False
        if self.__is_operand(token):
            if is_previous_character_operand:
                raise ParserException("Cannot have two operands in a row.")
            tokens_postfix.append(token)
            return True
        raise ParserException(f"Invalid token in expression: {token}")

    def __handle_close_bracket(self, operators_stack: List[Union[Operator, str]],
                               tokens_postfix: List[Union[Operator, str]]) -> None:
        """
        Handles the logic when a closing bracket is encountered during the conversion of an expression to postfix notation.
        :param operators_stack: The stack currently storing operators and open brackets.
        :param tokens_postfix: The current postfix token list being constructed.
        :raises ParserException: If there is a mismatched parenthesis.
        """
        while operators_stack:
            top = operators_stack.pop()
            if self.__is_open_bracket(top):
                break
            tokens_postfix.append(top)
        else:  # This else corresponds to the while, it executes if no break occurs (no open bracket found)
            raise ParserException("Mismatched parentheses in expression.")

    def __handle_operator(self, operator: Operator, operators_stack: List[Union[Operator, str]],
                          tokens_postfix: List[Union[Operator, str]]) -> None:
        """
        Handles the logic when an operator is encountered during the conversion of an expression to postfix notation.
        This includes applying the operator precedence rules.
        :param operator: The operator encountered.
        :param operators_stack: The stack currently storing operators and open brackets.
        :param tokens_postfix: The current postfix token list being constructed.
        """
        while operators_stack and isinstance(operators_stack[-1], Operator) and self.__does_have_higher_precedence(
                operators_stack[-1], operator):
            tokens_postfix.append(operators_stack.pop())
        operators_stack.append(operator)

    def __find_operator(self, token: str, operator_type: OperatorType) -> Optional[Operator]:
        """
        Finds an operator from the list of valid operators based on its symbol and type.
        :param token: The symbol of the operator to find.
        :param operator_type: The type of the operator (Unary/Binary).
        :return: The Operator object if found, None otherwise.
        """
        return next((op for op in self.operators if op.symbol == token and op.type == operator_type), None)

    def syntax_tree(self, expression: str) -> Node:
        """
        Parses the given algebraic expression and converts it into a syntax tree.
        :param expression: The algebraic expression to parse.
        :return: The root node of the syntax tree representing the given expression.
        :raises ParserException: If the expression is invalid or cannot be parsed into a valid syntax tree.
        """
        tokens = self.__tokenize(expression)
        postfix: List[Union[str, Operator]] = self.__postfix(tokens)
        stack = []
        for token in postfix:
            if isinstance(token, Operator):
                node = Node(token.symbol)
                if token.type == OperatorType.UNARY:
                    if len(stack) < 1:
                        raise ParserException("Unary operator has no operand.")
                    node.right = stack.pop()
                if token.type == OperatorType.BINARY:
                    if len(stack) < 2:
                        raise ParserException("Binary operator doesn't have 2 operands.")
                    node.right = stack.pop()
                    node.left = stack.pop()
            else:
                node = Node(token)
            stack.append(node)
        return stack.pop()

    @classmethod
    def evaluate(cls, node: Optional[Node], get_cell_value: Callable[[str], float]) -> float:
        """
        Recursively evaluates the syntax tree from the given node.
        :param node: Root of the syntax tree to evaluate.
        :param get_cell_value: Function that retrieves the value of a cell given its location identifier,
                               used to resolve cell references encountered in the expression tree.
        :return: Evaluated result as a float.
        :raises ParserException: If the provided node is None or if evaluation fails due to invalid structure.
        """
        if node is None:
            raise ParserException("Empty expression.")
        if node.is_leaf():
            return cls.__evaluate_leaf_node(node, get_cell_value)
        return cls.__evaluate_internal_node(node, get_cell_value)

    @staticmethod
    def __evaluate_leaf_node(node: Node, get_cell_value: Callable[[str], float]) -> float:
        """
        Evaluates a leaf node.
        :param node: The leaf node to evaluate.
        :param get_cell_value: Retrieves the value of a cell given its location identifier.
        :return: The numerical value associated with the leaf node.
        :raises ParserException: If the leaf node contains an invalid value.
        """
        if isinstance(node.value, float):
            return node.value
        elif isinstance(node.value, str):
            return get_cell_value(node.value)
        else:
            raise ParserException(f"Invalid leaf value: {node.value}")

    @classmethod
    def __evaluate_internal_node(cls, node: Node, get_cell_value: Callable[[str], float]) -> float:
        """
        Evaluates an internal (non-leaf) node.

        :param node: The internal node to evaluate.
        :param get_cell_value: Retrieves the value of a cell given its location identifier.
        :return: The result of evaluating the operation represented by the node.
        :raises ParserException: If the node contains an unsupported value or operation.
        """
        if not isinstance(node.value, Operator):
            raise ParserException(f"Unsupported node value: {node.value}")
        left_val = cls.evaluate(node.left, get_cell_value) if node.left else None
        right_val = cls.evaluate(node.right, get_cell_value) if node.right else None
        if node.value.type == OperatorType.UNARY:
            if right_val is None:
                raise ParserException("Missing operand for unary operator.")
            return node.value.calculate(right_val)
        elif node.value.type == OperatorType.BINARY:
            if left_val is None or right_val is None:
                raise ParserException("Missing operands for binary operator.")
            return node.value.calculate(right_val, left_val)
        else:
            raise ParserException(f"Unsupported operator type: {node.value.type}")


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
