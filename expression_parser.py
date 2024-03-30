import re
from typing import Optional, List, Union, Tuple

from exceptions import ParserException
from math_operator import MathOperator, UnaryOperator, BinaryOperator, Associativity, RangeOperator
from node import Node


class ExpressionParser:
    """
    Algebraic expression parser that converts algebraic expressions into a syntax tree or postfix notation.

    This parser supports a wide range of mathematical operations, including unary and binary operators, and
    special functionalities such as range operations within a specified context (e.g., spreadsheet formulas).
    It can handle complex expressions involving variables, numbers, and predefined functions, encapsulated
    within a flexible and extendable architecture. The parser is designed to work closely with custom `Node`
    objects representing individual components of the syntax tree for further evaluation or manipulation.

    The initialization of the parser requires a list of mathematical operators, which define the operational
    context, and regular expression patterns for identifying variables and ranges within the expressions.
    This design allows for easy adaptation to different contexts and customizability of the parsing logic.

    Usage involves creating an instance of the `ExpressionParser` with the desired configuration and then
    invoking the `syntax_tree` method with the algebraic expression to parse. The result is a `Node` object
    that represents the root of the syntax tree, ready for evaluation or analysis.

    Example:
        math_operators = [BinaryOperator("+", 1, Associativity.LTR), UnaryOperator("-", 2, Associativity.RTL)]
        var_pattern = re.compile(r"^[A-Z]+[0-9]+$")
        range_pattern = re.compile(r"^[A-Z]+[0-9]+:[A-Z]+[0-9]+$")
        parser = ExpressionParser(math_operators, var_pattern, range_pattern)
        root_node = parser.syntax_tree("A1+B2")

    Note:
        The class is part of a larger system for parsing and evaluating algebraic expressions, typically
        used within applications like spreadsheet software or custom calculation tools.

    Attributes:
        __operators (List[MathOperator]): A list of Operator objects that are valid in the expressions
            this parser will parse.
        __pattern (re.Pattern): A compiled regular expression used to match variable locations within
            the expressions.
        __range_pattern (re.Pattern): A compiled regular expression used to match range expressions.

    Raises:
        ParserException: If the expression is invalid or cannot be parsed into a valid syntax tree.
    """

    def __init__(self, math_operators: List[MathOperator], var_pattern: re.Pattern, range_pattern: re.Pattern) -> None:
        """
        Initializes the ExpressionParser with a list of operators.
        :param math_operators: A list of Operator objects that are valid in the expressions this parser will parse.
        """
        self.__operators = math_operators
        self.__pattern = var_pattern
        self.__range_pattern = range_pattern

    def __is_operator(self, token):
        """
        Checks whether the given token equals a symbol of a valid operator.
        :param token: The string to check.
        :return: True if the token is an operator, False otherwise.
        """
        return any(op.symbol == token for op in self.__operators)

    def __is_operand(self, string: str) -> bool:
        """Checks whether the given string is a valid operand."""
        return self.__is_number(string) or self.__is_location(string) or self.__is_range_token(string)

    def __is_location(self, string: str) -> bool:
        """
        Checks whether a string is in the format of a valid location in the sheet,
        which is a column string of capital letters, followed by a row number.
        """
        return bool(self.__pattern.match(string))

    def __is_range_token(self, string: str) -> bool:
        return bool(self.__range_pattern.match(string))

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
        :return: The longest valid token starting from the start_index.
        Returns an empty string if no valid token is found.
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
    def __does_have_higher_precedence(operator1: MathOperator, operator2: MathOperator) -> bool:
        """
        Determines if the second (current) operator has higher precedence than the first (previous) operator.
        This is dependent on the operator's associativity and precedence.
        If the second operator is left-to-right associative and its precedence is less than or equal to that of the
        first, or if the second operator is right-to-left associative and its precedence is less than that of the first,
        then the second operator is considered to have higher precedence.

        :param operator1: The first operator (previously on the stack).
        :param operator2: The second operator (currently being considered).
        :return: True if the second operator has higher precedence, False otherwise.
        """
        return (operator2.associativity == Associativity.LTR and operator2.precedence <= operator1.precedence) or (
                operator2.associativity == Associativity.RTL and operator2.precedence < operator1.precedence)

    def __postfix(self, tokens: List[str]) -> List[Union[MathOperator, str]]:
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
        tokens_postfix: List[Union[MathOperator, str, float]] = []  # The returned tokens in a postfix order.
        operators_stack: List[Union[MathOperator, str]] = []  # Stores Operator instances, and parentheses strings.
        # Filter spaces from the tokens list.
        filtered_tokens: List[str] = [token for token in tokens if not token.isspace()]
        # Initializing state of previous token.
        is_prev_operand = False
        is_prev_open_bracket = False
        # Updating the postfix tokens list and the operator stack for each given token.
        token_index = 0
        while token_index < len(filtered_tokens):
            is_prev_operand, is_prev_open_bracket, token_index = self.__process_token_postfix(token_index,
                                                                                              filtered_tokens,
                                                                                              operators_stack,
                                                                                              tokens_postfix,
                                                                                              is_prev_operand,
                                                                                              is_prev_open_bracket)
        # Handling the remaining tokens in the stack.
        while operators_stack:
            operator: Union[MathOperator, str] = operators_stack.pop()
            if isinstance(operator, str) and self.__is_bracket(operator):
                raise ParserException("Operator stack should not contain any brackets at this point!")
            tokens_postfix.append(operator)
        if not is_prev_operand:
            raise ParserException("The expression must end with an operand.")
        return tokens_postfix

    def __process_token_postfix(self, token_index: int, tokens: List[str],
                                operators_stack: List[Union[MathOperator, str]],
                                tokens_postfix: List[Union[MathOperator, str, float]],
                                is_previous_token_operand: bool,
                                is_previous_token_open_bracket: bool) -> Tuple[bool, bool, int]:
        """
        Processes a single token in the postfix logic.
        :param token_index: index of the current token in the tokens list.
        :param tokens: The list of tokens in the formula.
        :param operators_stack: A stack (implemented as a list) holding operators and parentheses during conversion.
        :param tokens_postfix: The list accumulating the postfix representation tokens.
        :param is_previous_token_operand: Flag indicating if the preceding token in the sequence was an operand.
        :param is_previous_token_open_bracket: Flag indicating if the preceding token was an open bracket.
        :return: 2 bool variables that indicate whether the current token is an operand (or a close bracket of an
            operand), and whether the current token is an open bracket.
            These flags are returned so that the next iteration is aware of the previous token state.
        :raises ParserException: Whether the token's arrangement breaks rules.
        """
        token = tokens[token_index]
        if self.__is_open_bracket(token):
            if is_previous_token_operand:
                raise ParserException("An open bracket cannot directly follow an operand.")
            operators_stack.append(token)
            return False, True, token_index + 1
        if self.__is_close_bracket(token):
            if is_previous_token_open_bracket:
                raise ParserException("Empty brackets are not allowed")
            self.__handle_close_bracket(token, operators_stack, tokens_postfix)
            return True, False, token_index + 1
        if self.__is_operator(token):
            operator = self.__find_operator(token, is_previous_token_operand)
            if operator is None:
                raise ParserException("Invalid operator in expression.")
            if isinstance(operator, RangeOperator):
                self.__handle_range_func(operator, token_index, tokens, tokens_postfix)
                token_index += 4
                return True, False, token_index
            else:
                self.__handle_operator(operator, operators_stack, tokens_postfix)
                return False, False, token_index + 1
        if self.__is_number(token):
            if is_previous_token_operand:
                raise ParserException("Cannot have two operands in a row.")
            tokens_postfix.append(float(token))
            return True, False, token_index + 1
        if self.__is_location(token):
            if is_previous_token_operand:
                raise ParserException("Cannot have two operands in a row.")
            tokens_postfix.append(token)
            return True, False, token_index + 1
        raise ParserException(f"Invalid token in expression: {token}")

    def __handle_close_bracket(self, close_bracket: str, operators_stack: List[Union[MathOperator, str]],
                               tokens_postfix: List[Union[MathOperator, str]]) -> None:
        """
        Handles the logic when a closing bracket is encountered during the conversion of an expression to postfix
        notation.
        :param close_bracket: A close bracket token string.
        :param operators_stack: The stack currently storing operators and open brackets.
        :param tokens_postfix: The current postfix token list being constructed.
        :raises ParserException: If there is a mismatched parenthesis.
        """
        current_brackets_remaining_operators = []
        while operators_stack and not self.__is_open_bracket(operators_stack[-1]):
            current_brackets_remaining_operators.append(operators_stack.pop())
        if len(operators_stack) == 0:
            raise ParserException("No open bracket found.")
        open_bracket = operators_stack.pop()
        if not self.__are_parentheses_pairs(open_bracket, close_bracket):
            raise ParserException("Mismatched parentheses in expression.")
        tokens_postfix.extend(current_brackets_remaining_operators)

    def __handle_operator(self, operator: MathOperator, operators_stack: List[Union[MathOperator, str]],
                          tokens_postfix: List[Union[MathOperator, str]]) -> None:
        """
        Handles the logic when an operator is encountered during the conversion of an expression to postfix notation.
        This includes applying the operator precedence rules.
        :param operator: The operator encountered.
        :param operators_stack: The stack currently storing operators and open brackets.
        :param tokens_postfix: The current postfix token list being constructed.
        """
        while operators_stack and isinstance(operators_stack[-1], MathOperator) and self.__does_have_higher_precedence(
                operators_stack[-1], operator):
            tokens_postfix.append(operators_stack.pop())
        operators_stack.append(operator)

    def __find_operator(self, token: str, is_previous_character_operand: bool) -> Optional[MathOperator]:
        """
        Finds an operator from the list of valid operators based on its symbol and the context.
        :param token: The symbol of the operator to find.
        :param is_previous_character_operand: Indicates whether the previous token is an operand (determines unary/binary).
        :return: The Operator object if found, None otherwise.
        """
        filtered_operators = [op for op in self.__operators if op.symbol == token]

        range_op = next((op for op in filtered_operators if isinstance(op, RangeOperator)), None)
        if range_op is not None:
            return range_op
        binary_op = next((op for op in filtered_operators if isinstance(op, BinaryOperator)), None)
        unary_op = next((op for op in filtered_operators if isinstance(op, UnaryOperator)), None)
        return binary_op if is_previous_character_operand and binary_op else unary_op

    def syntax_tree(self, expression: str) -> Node:
        """
        Parses the given algebraic expression and converts it into a syntax tree.
        :param expression: The algebraic expression to parse.
        :return: The root node of the syntax tree representing the given expression.
        :raises ParserException: If the expression is invalid or cannot be parsed into a valid syntax tree.
        """
        tokens = self.__tokenize(expression)
        postfix: List[Union[str, MathOperator]] = self.__postfix(tokens)
        if len(postfix) == 0:
            raise ParserException("Postfix list is empty!")
        stack = []
        for token in postfix:
            node = Node(token)
            if isinstance(token, MathOperator):
                if isinstance(token, (UnaryOperator, RangeOperator)):
                    if len(stack) < 1:
                        raise ParserException("Unary operator has no operand.")
                    node.right = stack.pop()
                elif isinstance(token, BinaryOperator):
                    if len(stack) < 2:
                        raise ParserException("Binary operator doesn't have 2 operands.")
                    node.right = stack.pop()
                    node.left = stack.pop()
            stack.append(node)
        return stack.pop()

    def __handle_range_func(self, operator: RangeOperator, token_index: int, tokens: List[str],
                            tokens_postfix: List[Union[MathOperator, str]]) -> None:
        """
       Validates and appends a range function to the postfix tokens list.

       Ensures the range function, starting at `token_index`, follows the correct structure:
       an opening bracket, a valid range token, and a closing bracket. If valid, appends the
       range token and its operator to `tokens_postfix`.

       :param operator: The RangeOperator to process.
       :param token_index: Index of the range operator in `tokens`.
       :param tokens: List of all tokens from the expression.
       :param tokens_postfix: Postfix tokens list being populated.
       :raises ParserException: If the range function format is incorrect or tokens are missing.
       """
        if token_index > len(tokens) - 4:
            raise ParserException("missing range tokens.")
        open_bracket, range_token, close_bracket = tokens[token_index + 1: token_index + 4]
        if all([self.__is_open_bracket(open_bracket), self.__is_close_bracket(close_bracket),
                self.__are_parentheses_pairs(open_bracket, close_bracket), self.__is_range_token(range_token)]):
            tokens_postfix.append(range_token)
            tokens_postfix.append(operator)
        else:
            raise ParserException("Bad range function call format.")
