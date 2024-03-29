import csv
import json
import re
from typing import Dict, Tuple, Union, Optional, List, Set

import networkx as nx

from cell import Cell
from exceptions import CircularDependenciesException, ParserException, EvaluationException, BadNameException, \
    SheetLoadException
from expression_parser import ExpressionParser
from failure_reason import FailureReason
from math_operator import Plus, Minus, Times, Divide, Negate, Sin, Power, MathOperator, UnaryOperator, BinaryOperator, \
    Max, Min, Sum, Average, RangeOperator
from node import Node

Position = Tuple[int, int]  # (Row Index, Column Index)
Content = Union[str, float, Node]
Value = Union[str, float]


class Sheet:
    __EQUATION_PREFIX = "="
    # Column names consts.
    __NUMBER_OF_LETTERS = 26
    __A_ASCII = 65
    # Storing compiled regex patterns (identical in the class level), and regex groups to query later.
    # Cell pattern.
    __CELL_PATTERN: re.Pattern = re.compile("^(?P<column>[A-Z]+)(?P<row>[0-9]+)$")
    __COLUMN_PATTERN_GROUP = "column"
    __ROW_PATTERN_GROUP = "row"
    # Cells range pattern.
    __RANGE_NAME_PATTERN: re.Pattern = re.compile("^(?P<col1>[A-Z]+)(?P<row1>[0-9]+):(?P<col2>[A-Z]+)(?P<row2>[0-9]+)$")
    __COL1_GROUP = "col1"
    __COL2_GROUP = "col2"
    __ROW1_GROUP = "row1"
    __ROW2_GROUP = "row2"

    # Storage consts.
    __CSV_EXTENSION = '.csv'
    __JSON_EXTENSION = '.json'
    # The sheet currently support a fixed size that usually fits a laptop screen.
    ROWS_NUM: int = 20
    COLUMNS_NUM: int = 10

    def __init__(self, json_file: Optional[str] = None):
        """
        A class that holds sheet data. It allows updates and storage to files.
        :param json_file: If given, load the initial data from a json file.
        :raise FileNotFoundError, json.JSONDecodeError, PermissionError, TypeError: If json read fails.
        :raise SheetLoadException: If json data cannot be loaded as a valid sheet.
        """
        self.__parser = ExpressionParser(math_operators=[Plus(), Minus(), Times(), Divide(), Negate(), Sin(), Power(),
                                                         Max(), Min(), Sum(), Average()],
                                         var_pattern=self.__CELL_PATTERN, range_pattern=self.__RANGE_NAME_PATTERN)
        self.__cells: Dict[Position, Cell] = {}
        self.__cells_values: Dict[Position, Value] = {}  # Allows retrieving values without reevaluation.
        self.__dependencies_graph = nx.DiGraph()  # Stores the dependencies between cells (formulas).
        if json_file is not None:
            # Raises errors to caller.
            data: Dict[Position, str] = self.__load_data_from_json(json_file)
            self.__cells: Dict[Position, Cell] = {position: Cell(content, self.__parse_content(content)) for
                                                  position, content in data.items()}
            self.__dependencies_graph, self.__cells_values = self.__evaluate_cells(self.__cells)

    def __evaluate_cells(self, cells: Dict[Position, Cell]):
        """
        Initial cells evaluation - evaluate all loaded cells in a single computations.
        Takes into consideration graph cycles and evaluation by the reverse topological order of the dependencies,
        i.e. evaluating each item only after its dependencies are evaluated.
        """
        dependency_graph = nx.DiGraph()
        for position, cell in cells.items():
            content = cell.get_parsed_content()
            dependencies = self.__get_dependencies(content) if isinstance(content, Node) else set()
            graph_edges = [(position, dependency) for dependency in dependencies]
            dependency_graph.add_edges_from(graph_edges)
            try:
                list(nx.topological_sort(dependency_graph))
            except nx.NetworkXUnfeasible:
                raise CircularDependenciesException("Cycle detected, new edges not added.")
        for position in cells.keys():
            # Adding all positions given, so all cells weill be evaluated, even if they don't have any dependencies.
            # Will remove isolates from graph later.
            dependency_graph.add_node(position)
        # Each item depends only on previous items in the order. There are no cycles at this point.
        reverse_topological_order: List[Position] = list(nx.topological_sort(dependency_graph.reverse()))
        values: Dict[Position, Value] = {}
        for position in reverse_topological_order:
            values[position] = self.__evaluate_position(position, values)
        self.__remove_isolates(dependency_graph)
        return dependency_graph, values

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

    def get_cell_name(self, col_index: int, row_index: int) -> str:
        row_name: str = self.row_index_to_name(row_index)
        col_name: str = self.column_index_to_name(col_index)
        return f"{col_name}{row_name}"

    def try_update(self, row_index: int, col_index: int, written_content: str) -> Tuple[
        bool, Dict[Position, Optional[Value]], Optional[FailureReason]]:
        """
        Tries to evaluate the given content and update the sheet with its evaluation in the given position.
        Returns whether the update was successful, and if so - the values to update in the GUI.
        A valid content is a valid string / number value, or a parsable formula that does not create
        a dependency cycle with other existing cells. If the content is not valid - and error is raised.

        Note - If there is a None value in the dict of updated positions returned, it means that the cell was deleted.
        It happens when given an empty string, which means deleting the cell.
        This is done to not store empty / deleted values.
        """
        try:
            current_position: Position = (row_index, col_index)
            content: Content = self.__parse_content(written_content)

            # Compute dependents to update, and validate no cycles in the dependency graph.
            updated_position_dependencies = self.__get_dependencies(content) if isinstance(content, Node) else set()
            new_dependency_graph: nx.DiGraph = self.__get_updated_graph(current_position, updated_position_dependencies)
            dependents_to_reevaluate: List[Position] = self.__compute_dependencies(current_position,
                                                                                   new_dependency_graph)

            # If new content is empty, treat it as a delete operation.
            if content == "":
                self.__delete_position(current_position, dependents_to_reevaluate)
                return True, {current_position: None}, None

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
        except ZeroDivisionError:
            return False, {}, FailureReason.ZERO_DIVISION
        except Exception:
            return False, {}, FailureReason.UNEXPECTED_EXCEPTION

    def __get_dependencies(self, node: Node) -> Set[Position]:
        """
        Given a node, iterates over its string nodes returns set of positions.
        :raises EvaluationException: If a cell name cannot be converted to a position.
        """
        dependencies: Set[Position] = set()
        for string_token in self.__get_string_nodes(node):
            if self.__CELL_PATTERN.match(string_token):
                dependencies.add(self.__cell_name_to_location(string_token))
            elif self.__RANGE_NAME_PATTERN.match(string_token):
                range_positions: Set[Position] = self.__calculate_range_positions(string_token)
                dependencies.update(range_positions)
        return dependencies

    def __delete_position(self, position: Position, dependent_positions: List[Position]):
        """Deletes cell data from the sheet if it is not a dependency of any other cell. If it doesn't exist - skip."""
        if dependent_positions:
            raise EvaluationException("Cannot delete cell when another cell is dependent on it.")
        self.__cells.pop(position, None)  # Remove if exists.
        self.__cells_values.pop(position, None)  # Remove if exists.

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
    def __try_parse_number(value: str) -> Optional[float]:
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

    @classmethod
    def __cell_name_to_location(cls, cell_name: str) -> Position:
        """
        Convert a cell name (like 'A1', 'B2', etc.) to its corresponding row and column indices.
        :raises EvaluationException: If the cell name does not match the regular expression.
        :return: A tuple of a row index followed by a column index.
        """
        match = cls.__CELL_PATTERN.match(cell_name)
        if not match:
            raise BadNameException(f"Invalid cell name format: {cell_name}")
        # Accessing named groups directly for better readability
        column_part = match.group(cls.__COLUMN_PATTERN_GROUP)
        row_part = match.group(cls.__ROW_PATTERN_GROUP)
        position = (cls.__row_name_to_index(row_part), cls.__column_name_to_index(column_part))
        if not cls.__position_in_sheet_range(position):
            raise BadNameException("Cell indexes outside of range.")
        return position

    @classmethod
    def __row_name_to_index(cls, row_name: str):
        """Subtract one from row index to start from 0, and convert row_part from string to integer"""
        return int(row_name) - 1

    @classmethod
    def __column_name_to_index(cls, column_name: str):
        """Compute Ascii value of each letter in the column name."""
        column_ascii_list = [(ord(char) - cls.__A_ASCII) for char in column_name]
        return sum([char_index * cls.__NUMBER_OF_LETTERS + char_ascii
                    for (char_index, char_ascii) in enumerate(column_ascii_list)])

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
        self.__remove_isolates(new_dependency_graph)
        return new_dependency_graph

    @staticmethod
    def __remove_isolates(dependency_graph: nx.DiGraph):
        """Find all isolated items (nodes with no edges) and remove them, since they no longer have any meaning."""
        isolated_items = list(nx.isolates(dependency_graph))
        dependency_graph.remove_edges_from(isolated_items)

    @staticmethod
    def __compute_dependencies(current_position: Position, dependency_graph: nx.DiGraph) -> List[Position]:
        """
        Attempt a topological sort to check for cycles in the graph. # TODO - elaborate.
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
                dependents: Set[Position] = nx.descendants(dependency_graph.reverse(), current_position)
                return [position for position in reversed(total_order) if position in dependents]
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
        if isinstance(node.value, RangeOperator):
            if not (isinstance(node.right.value, str) and node.left is None):
                raise EvaluationException("Problem evaluating a Range Operator node.")
            range_positions: Set[Position] = self.__calculate_range_positions(node.right.value)
            range_values: List[Value] = [self.__evaluate_position(position, cache) for position in range_positions]
            if any(isinstance(v, str) for v in range_values):
                raise EvaluationException("Can't run range functions on string operands.")
            return node.value.calculate(range_values)
        # Retrieve values for left and right children if they exist.
        left_val: Optional[Value] = self.__evaluate(node.left, cache) if node.left else None
        right_val: Optional[Value] = self.__evaluate(node.right, cache) if node.right else None
        if isinstance(left_val, str) or isinstance(left_val, str):
            raise EvaluationException("Child nodes must have number evaluations.")
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

    def try_save(self, file_name: str) -> bool:
        """
        Determine in which format to save the file.
        :param file_name: The path to the file where the sheet should be saved, can be absolute or relative.
        :return: True if the file was saved successfully, False otherwise.
        """
        if file_name.endswith(self.__CSV_EXTENSION):
            return self.__save_as_csv(file_name)
        if file_name.endswith(self.__JSON_EXTENSION):
            return self.__save_as_json(file_name)
        # The file name doesn't contain valid extension
        return False

    def __save_as_csv(self, file_name: str) -> bool:
        """
        Saves the sheet's current state as a CSV file, formatted like a table without explicit row and column indices.
        """
        try:
            with open(file_name, mode='w', newline='') as file:
                csv_writer = csv.writer(file)
                grid = self.__to_csv_table()
                for row in grid:
                    csv_writer.writerow(row)
            return True
        except Exception:
            return False

    def __to_csv_table(self) -> List[List[str]]:
        """Convert stored sheet data to a matrix of string values."""
        grid = [["" for _ in range(self.COLUMNS_NUM)] for _ in range(self.ROWS_NUM)]
        for (row_index, column_index), value in self.__cells_values.items():
            grid[row_index][column_index] = f'"{value}"' if isinstance(value, str) and "," in value else value
        return grid

    def __save_as_json(self, file_name: str) -> bool:
        """
        Saves the sheet's current state as a JSON file.
        """
        try:
            with open(file_name, mode='w') as file:
                json.dump(self.__to_json_format(), file, indent=4)
            return True
        except Exception:
            return False

    def __to_json_format(self) -> Dict[str, str]:
        """
        Converts stored sheet data to a dictionary suitable for JSON serialization.
        """
        data: Dict[str, str] = {}
        for (row_index, column_index), cell in self.__cells.items():
            cell_content = cell.get_content()
            data[self.get_cell_name(column_index, row_index)] = cell_content
        return data

    def __load_data_from_json(self, json_file_name: str) -> Dict[Position, str]:
        """
        Parses sheet data from a json file.
        :param json_file_name: The path to the JSON file.
        :return: A mapping between cell positions in the sheet and Cell instances.
        """
        cells: Dict[Position, str] = {}
        with open(json_file_name, "r") as file:
            data: Dict[str, str] = json.load(file)
            for cell_name, cell_content in data.items():
                if not isinstance(cell_name, str) or not isinstance(cell_content, str):
                    raise SheetLoadException("Json file must contain string keys and string values only.")
                row, column = self.__cell_name_to_location(cell_name)
                cells[(row, column)] = cell_content
        return cells

    @classmethod
    def __calculate_range_positions(cls, range_value: str) -> Set[Position]:
        match = cls.__RANGE_NAME_PATTERN.match(range_value)
        if not match:
            raise BadNameException(f"Invalid cells range name format: {range_value}")
        row1_name = match.group(cls.__ROW1_GROUP)
        col1_name = match.group(cls.__COL1_GROUP)
        start_position = cls.__row_name_to_index(row1_name), cls.__column_name_to_index(col1_name)
        start_row_index, start_col_index = start_position
        row2_name = match.group(cls.__ROW2_GROUP)
        col2_name = match.group(cls.__COL2_GROUP)
        end_position = cls.__row_name_to_index(row2_name), cls.__column_name_to_index(col2_name)
        end_row_index, end_col_index = end_position
        # I return a set since the positions are unique.
        if not (cls.__position_in_sheet_range(start_position) and cls.__position_in_sheet_range(end_position)):
            raise BadNameException("Range is not inside the sheet.")
        if start_row_index == end_row_index and start_col_index <= end_col_index:
            return {(start_row_index, col) for col in range(start_col_index, end_col_index + 1)}
        elif start_col_index == end_col_index and start_row_index <= end_row_index:
            return {(row, start_col_index) for row in range(start_row_index, end_row_index + 1)}
        raise BadNameException("Range name is not a valid range.")

    @classmethod
    def __position_in_sheet_range(cls, position: Position) -> bool:
        row, col = position
        return 0 <= row < cls.ROWS_NUM and 0 <= col < cls.COLUMNS_NUM
