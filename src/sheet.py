import re
from enum import Enum, auto
from typing import Dict, Tuple, Union, Optional, List, Set

import networkx as nx

from cell import Cell
from exceptions import CircularDependenciesException, ParserException, EvaluationException, BadNameException
from expression_parser import ExpressionParser
from math_operator import Plus, Minus, Times, Divide, Negate, Sin, Power, MathOperator, UnaryOperator, BinaryOperator
from node import Node


# TODO list
#  1. If a cell gets deleted, do not store an empty string. make a delete_cell method.
#  2. Update GUI to support larger sheets, then check high column naming (also use "=AB13" in a formula).

# TODO - deside what to do with strings in formulas.
#  handle string + float case, and define string + string or string * int behavior.
#  It acts wierd and only sometimes work.
#  Currently I simply do not allow string values in formulas.

# TODO - refactor long try-catch flow (I don't have a good idea).

class FailureReason(Enum):
    DEPENDENCIES_CYCLE = auto()
    COULD_NOT_PARSE = auto()
    UNEXPECTED_EXCEPTION = auto()
    EVALUATION_FAILURE = auto()
    BAD_NAME_REFERENCE = auto()


Position = Tuple[int, int]  # (Row Index, Column Index)
Content = Union[str, float, Node]
Value = Union[str, float]


class Sheet:
    __EQUATION_PREFIX = "="
    # Column names consts.
    __NUMBER_OF_LETTERS = 26
    __A_ASCII = 65
    __COLUMN_PATTERN_GROUP = "column"
    __ROW_PATTERN_GROUP = "row"

    def __init__(self, rows_number: int, columns_number: int):
        self.__rows_num: int = rows_number
        self.__columns_num: int = columns_number
        pattern_str = '^(?P<{column}>[A-Z]+)(?P<{row}>[0-9]+)$'.format(column=self.__COLUMN_PATTERN_GROUP,
                                                                       row=self.__ROW_PATTERN_GROUP)
        self.__CELL_PATTERN = re.compile(pattern_str)
        self.__cell_name_pattern: re.Pattern = \
            re.compile(fr"^(?P<{self.__COLUMN_PATTERN_GROUP}>[A-Z]+)(?P<{self.__ROW_PATTERN_GROUP}>[0-9]+)$")
        # Sheet state:
        self.__cells: Dict[Position, Cell] = {}
        self.__cells_values: Dict[Position, Value] = {}  # Allows retrieving values without reevaluation.
        self.__parser = ExpressionParser(math_operators=[Plus(), Minus(), Times(), Divide(), Negate(), Sin(), Power()],
                                         var_pattern=self.__cell_name_pattern)
        self.__dependencies_graph = nx.DiGraph()  # Stores the dependencies between cells (formulas).

    def get_rows_number(self) -> int:
        return self.__rows_num

    def get_columns_number(self) -> int:
        return self.__columns_num

    def get_cell_content(self, row_index: int, column_index: int) -> Optional[str]:
        """Get the content of the cell."""
        cell = self.__cells.get((row_index, column_index))
        if cell is None:
            return None
        return cell.get_content()

    def get_value(self, row_index: int, column_index: int) -> Optional[Value]:
        """Get the cached value of the cell."""
        return self.__cells_values.get((row_index, column_index))

    @staticmethod
    def row_index_to_name(row_index: int) -> str:
        """
        A string label representing the row, starting with "1" in the 0 index.
        """
        return str(row_index + 1)

    @classmethod
    def column_index_to_name(cls, col_index: int) -> str:
        """
        A string label representing the column, starting with "A".
        """
        name = ""
        while col_index >= 0:
            name += chr(col_index % cls.__NUMBER_OF_LETTERS + cls.__A_ASCII)
            col_index = col_index // cls.__NUMBER_OF_LETTERS - 1
        return name

    def try_update(self, row_index: int, col_index: int, written_content: str) -> Tuple[bool,
                                                                                        Dict[Position, Value],
                                                                                        Optional[FailureReason]]:
        """
        Tries to evaluate the given content and update the sheet with its evaluation in the given position.
        Returns whether the update was successful, and if so - the values to update in the GUI.
        A valid content is a valid string / number value, or a parsable formula that does not create
        a dependency cycle with other existing cells. If the content is not valid - and error is raised.
        """
        try:
            current_position: Position = (row_index, col_index)
            content: Content = self.__parse_content(written_content)

            # Compute dependents to update, and validate no cycles in the dependency graph.
            updated_position_dependencies = set()
            if isinstance(content, Node):
                cell_names: List[str] = self.__get_string_nodes(content)
                # Raises EvaluationException if a cell name cannot be converted to a position.
                updated_position_dependencies: Set[Position] = {self.__cell_name_to_location(d) for d in cell_names}
            new_dependency_graph: nx.DiGraph = self.__get_updated_graph(current_position, updated_position_dependencies)
            dependents_to_reevaluate: List[Position] = self.__compute_dependencies(current_position,
                                                                                   new_dependency_graph)

            # Evaluate / Reevaluate the current position value, then store the result in a caching dict.
            cached_results: Dict[Position, Value] = {}
            updated_value = self.__evaluate(content, cached_results) if isinstance(content, Node) else content
            cached_results[current_position] = updated_value
            positions_to_update: Dict[Position, Value] = {current_position: updated_value}
            # Evaluating current position dependents according to the dependency graph order.
            for position in dependents_to_reevaluate:
                positions_to_update[position] = self.__evaluate_position(position, cached_results)
            # If success - update the state of the dependency graph and the values cache.
            self.__cells[current_position] = Cell(written_content, content)
            self.__dependencies_graph = new_dependency_graph
            self.__cells_values.update(positions_to_update)
            return True, positions_to_update, None
        except BadNameException:
            return False, {}, FailureReason.BAD_NAME_REFERENCE
        except EvaluationException:
            return False, {}, FailureReason.EVALUATION_FAILURE
        except ParserException:
            return False, {}, FailureReason.COULD_NOT_PARSE
        except CircularDependenciesException:
            return False, {}, FailureReason.DEPENDENCIES_CYCLE
        except Exception:
            return False, {}, FailureReason.UNEXPECTED_EXCEPTION

    def __parse_content(self, cell_content: str) -> Content:
        """
        Converts a string content of a cell in the sheet to a parsed value that can be evaluated.
        :raises ParserException: If the cell content is an invalid formula that cannot be parsed.
        """
        number_result: Optional[float] = self.__try_parse_number(cell_content)
        if number_result is not None:
            return number_result
        if cell_content.startswith(self.__EQUATION_PREFIX):
            return self.__parser.syntax_tree(cell_content[1:])  # Returns a Node of an expression tree.
        return cell_content  # When the content is a simple string.

    @staticmethod
    def __try_parse_number(value: str) -> Optional[bool]:
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def __get_string_nodes(node: Node) -> List[str]:
        """
        Collects all nodes in the tree where the value is of type str.
        :return: A list of Nodes with string values.
        """
        return [node.value for node in node.preorder() if isinstance(node.value, str)]

    def __cell_name_to_location(self, cell_name: str) -> Position:
        """
        Convert a cell name (like 'A1', 'B2', etc.) to its corresponding row and column indices.
        :raises EvaluationException: If the cell name does not match the regular expression.
        :return: A tuple of a row index followed by a column index.
        """
        match = self.__cell_name_pattern.match(cell_name)
        if not match:
            raise BadNameException(f"Invalid cell name format: {cell_name}")
        # Accessing named groups directly for better readability
        column_part = match.group(self.__COLUMN_PATTERN_GROUP)
        row_part = match.group(self.__ROW_PATTERN_GROUP)
        # Compute Ascii value of each letter in the column name.
        column_ascii_list = [(ord(char) - self.__A_ASCII) for char in column_part]
        column_index = sum([char_index * self.__NUMBER_OF_LETTERS + char_ascii
                            for (char_index, char_ascii) in enumerate(column_ascii_list)])
        # Subtract one from row index to start from 0, and convert row_part from string to integer
        row_index = int(row_part) - 1
        return row_index, column_index

    def __get_updated_graph(self, position: Position,
                            position_dependencies: Optional[Set[Position]] = None) -> nx.DiGraph:
        """
        Return an updated graph with the new dependencies of the given position.
        If the position_dependencies is not given, the position is updated to have no dependencies (e.g. float cell).
        """
        updated_edges: Set[(Position, Position)] = \
            {(position, d) for d in position_dependencies} if position_dependencies is not None else set()
        # I edit a copy of the graph, so if there's an error I could revert to the original graph easily.
        new_dependency_graph: nx.DiGraph = self.__dependencies_graph.copy()
        # Update new dependencies and remove deleted dependencies from the temporary graph.
        new_dependency_graph.remove_edges_from(list(new_dependency_graph.out_edges(position)))
        new_dependency_graph.add_edges_from(updated_edges)
        # Find all isolated items (nodes with no edges) and remove them, since they no longer have any meaning.
        isolated_items = list(nx.isolates(new_dependency_graph))
        new_dependency_graph.remove_edges_from(isolated_items)
        return new_dependency_graph

    @staticmethod
    def __compute_dependencies(current_position: Position, dependency_graph: nx.DiGraph) -> List[Position]:
        """
        Attempt a topological sort to check for cycles in the graph.
        For further details on the algorithm, I recommend the following explanation:
        https://www.youtube.com/watch?v=WqV-pxNUAYA.
        :raises CircularDependenciesException: If there is a cycle in the graph.
        :return: The list of dependencies to evaluate in order to estimate the current position,
        and a list of the positions that are dependent on the current position, according to the topological-sort order.
        The returned list does not contain the current position itself.
        """
        try:
            # If there is a cycle in the graph, an exception is raised here.
            total_order = list(nx.topological_sort(dependency_graph))
            # Derive dependents_update_order by using the reversed graph's total order.
            if current_position in dependency_graph:
                reachable_from_current_in_reversed: Set[Position] = nx.descendants(dependency_graph.reverse(),
                                                                                   current_position)
                return [node for node in reversed(total_order) if node in reachable_from_current_in_reversed]
            return []
        except nx.NetworkXUnfeasible:
            raise CircularDependenciesException("Cycle detected, new edges not added.")

    def __evaluate_position(self, position: Position, evaluated_positions: Dict[Position, Value]) -> Value:
        # Attempt to fetch the updated results first (changes from the stored values).
        if position in evaluated_positions:
            return evaluated_positions[position]
        # If the position is not cached anywhere, compute its value.
        cell = self.__cells.get(position)
        if not cell:
            raise EvaluationException("Cell does not exist.")
        content = cell.get_parsed_content()
        value = self.__evaluate(content, evaluated_positions) if isinstance(content, Node) else content
        # Update the local cache, but not the sheet-level stored values yet.
        evaluated_positions[position] = value
        return value

    def __evaluate(self, node: Node, reevaluated_values: Dict[Position, Value]) -> Value:
        """
        Recursively evaluates the syntax tree from the given node, while updating the reevaluated_values with evaluated
         results.
        """
        if node.is_leaf():
            return self.__evaluate_leaf_node(node, reevaluated_values)
        return self.__evaluate_internal_node(node, reevaluated_values)

    def __evaluate_leaf_node(self, node: Node, cache: Dict[Position, Value]) -> Value:
        """
        Evaluates a leaf node, using the cache for cell references.
        """
        if isinstance(node.value, float):
            return node.value  # Directly return the numerical value.
        if isinstance(node.value, str):
            # Convert cell reference to position and fetch its value, using the cache.
            cell_position = self.__cell_name_to_location(node.value)
            return self.__evaluate_position(cell_position, cache)
        # If node's value isn't float or string, raise an exception.
        raise EvaluationException(f"Invalid leaf value: {node.value}")

    def __evaluate_internal_node(self, node: Node, cache: Dict[Position, Value]) -> Value:
        """
        Evaluates an internal (non-leaf) node, using the cache to avoid redundant calculations.
        """
        if not isinstance(node.value, MathOperator):
            raise EvaluationException(f"Unsupported node value: {node.value}")
        # Retrieve values for left and right children if they exist.
        left_val = self.__evaluate(node.left, cache) if node.left else None
        right_val = self.__evaluate(node.right, cache) if node.right else None
        if not isinstance(left_val, (float, int)) or not isinstance(left_val, (float, int)):
            raise EvaluationException("All values in a formula evaluation must be numbers.")
        # Handle unary and binary operations.
        if isinstance(node.value, UnaryOperator):
            if right_val is None:
                raise EvaluationException("Missing operand for unary operator.")
            return node.value.calculate(right_val)
        if isinstance(node.value, BinaryOperator):
            if left_val is None or right_val is None:
                raise EvaluationException("Missing operands for binary operator.")
            return node.value.calculate(left_val, right_val)
        # If the node's operator type is neither unary nor binary, raise an exception.
        raise EvaluationException(f"Unsupported operator type: {type(node.value)}")
