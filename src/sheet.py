import re
from typing import Dict, Tuple, Union, Optional

from cell import Cell
from math_operator import Plus, Minus, Times, Divide, Negate, Sin, Power, MathOperator, UnaryOperator, BinaryOperator
from node import Node
from expression_parser import ExpressionParser

Position = Tuple[int, int]  # (Row Index, Column Index)


class EvaluationException(Exception):
    # TODO - make an exceptions module.
    pass


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
        self.__cells: Dict[Position, Cell] = {}  # Dictionary to store cells with their coordinates
        pattern_str = '^(?P<{column}>[A-Z]+)(?P<{row}>[0-9]+)$'.format(column=self.__COLUMN_PATTERN_GROUP,
                                                                       row=self.__ROW_PATTERN_GROUP)
        self.__CELL_PATTERN = re.compile(pattern_str)
        self.__cell_name_pattern: re.Pattern = \
            re.compile(fr"^(?P<{self.__COLUMN_PATTERN_GROUP}>[A-Z]+)(?P<{self.__ROW_PATTERN_GROUP}>[0-9]+)$")
        self.__parser = ExpressionParser(math_operators=[Plus(), Minus(), Times(), Divide(), Negate(), Sin(), Power()],
                                         var_pattern=self.__cell_name_pattern)

    def get_rows_number(self) -> int:
        return self.__rows_num

    def get_columns_number(self) -> int:
        return self.__columns_num

    def __get_cell(self, row_index: int, column_index: int) -> Optional[Cell]:
        """Retrieve the cell object for the given row and column indexes."""
        return self.__cells.get((row_index, column_index))

    def get_cell_content(self, row_index: int, column_index: int) -> Optional[str]:
        """Get the content of the cell."""
        cell = self.__get_cell(row_index, column_index)
        if cell is None:
            return None
        return cell.get_content()

    def evaluate_position(self, row_index: int, column_index: int) -> Optional[Union[str, float]]:
        """Get the estimated value of the cell."""
        cell = self.__get_cell(row_index, column_index)
        if cell is None:
            return None
        return self.__evaluate_cell(cell)

    def __evaluate_cell(self, cell: Cell) -> Union[str, float]:
        parsed_content: Union[str, float, Node] = cell.get_parsed_content()
        return self.__evaluate(parsed_content) if isinstance(parsed_content, Node) else parsed_content

    def try_update(self, row_index: int, col_index: int, written_content: str) -> Tuple[bool, Dict[Position,
                                                                                                   Union[str, float]]]:
        # TODO if formula - handle + handle exceptions.
        # TODO - edge cases:
        #  1. New node is valid, new value is valid, but dependent equations will error on that value -
        #     like updating the value to 0 but an other cell divides by it.
        #  2. Trying to update to str but other formula depends on it.
        #  3. Formula inf dependency loops.
        #  4. New node is valid, but evaluation would fail for some reason, like ref to missing cell.
        # TODO - what happens when the Tree Node is created successfully,
        #  but it contains invalid locations like A1 which is a string or doesnt exist, or a range...
        #  Currently, assume that if the node is returned with no error - the tree is valid and can be computed.
        # old_cell = self.__cells.get((row_index, col_index))
        # dependencies: List[Position] = self.__get_dependencies(formula_root_node)

        parsed_content: Union[str, float, Node] = self.__parse_content(written_content)
        cell: Cell = Cell(written_content, parsed_content)
        value: Union[str, float] = self.__evaluate_cell(cell)
        loc = (row_index, col_index)
        updated_cells = {loc: value}
        success = True
        if success:
            self.__cells[loc] = cell
            print("AAA", {k: self.__evaluate_cell(v) for k, v in self.__cells.items()})  # todo - remove
            return True, updated_cells
        return False, {}

    def __parse_content(self, cell_content) -> Union[str, float, Node]:
        number_result: Optional[float] = self.__try_parse_number(cell_content)
        if number_result is not None:
            return number_result
        if cell_content.startswith(self.__EQUATION_PREFIX):
            try:
                formula = cell_content[1:]
                formula_root_node: Node = self.__try_parse_formula(formula)
                return formula_root_node
            except Exception as e:  # TODO Consider only Parse Exception.
                raise  # TODO - handle exceptions!
        return cell_content  # When the content is a simple string.

    @staticmethod
    def __try_parse_number(value: str) -> Optional[bool]:
        try:
            return float(value)
        except ValueError:
            return None

    def __try_parse_formula(self, content) -> Node:
        """TODO Handle error cases."""
        return self.__parser.syntax_tree(content)

    def __evaluate(self, node: Optional[Node]) -> float:
        """
        Recursively evaluates the syntax tree from the given node.
        :param node: Root of the syntax tree to evaluate.
        :return: Evaluated result as a float.
        :raises EvaluationException: If the provided node is None or if evaluation fails due to invalid structure.
        """
        if node is None:
            raise EvaluationException("Empty expression.")
        if node.is_leaf():
            return self.__evaluate_leaf_node(node)
        return self.__evaluate_internal_node(node)

    def __evaluate_leaf_node(self, node: Node) -> float:
        """
        Evaluates a leaf node.
        :param node: The leaf node to evaluate.
        :return: The numerical value associated with the leaf node.
        :raises EvaluationException: If the leaf node contains an invalid value.
        """
        if isinstance(node.value, float):
            return node.value
        elif isinstance(node.value, str):
            return self.__get_cell_value(node.value)
        else:
            raise EvaluationException(f"Invalid leaf value: {node.value}")

    def __get_cell_value(self, cell_location: str) -> float:
        row_index, column_index = self.__cell_name_to_location(cell_location)  # TODO - handle exception raised here.
        value: Optional[float, str] = self.evaluate_position(row_index, column_index)
        if value is None:
            raise EvaluationException("Cell does not contain a value.")
        if isinstance(value, (float, int)):
            return value
        raise EvaluationException("Cell contains unexpected value type.")

    def __evaluate_internal_node(self, node: Node) -> float:
        """
        Evaluates an internal (non-leaf) node.
        :param node: The internal node to evaluate.
        :return: The result of evaluating the operation represented by the node.
        :raises EvaluationException: If the node contains an unsupported value or operation.
        """
        if not isinstance(node.value, MathOperator):
            raise EvaluationException(f"Unsupported node value: {node.value}")
        left_val = self.__evaluate(node.left) if node.left else None
        right_val = self.__evaluate(node.right) if node.right else None
        if isinstance(node.value, UnaryOperator):
            if right_val is None:
                raise EvaluationException("Missing operand for unary operator.")
            return node.value.calculate(right_val)
        elif isinstance(node.value, BinaryOperator):
            if left_val is None or right_val is None:
                raise EvaluationException("Missing operands for binary operator.")
            return node.value.calculate(left_val, right_val)
        else:
            raise EvaluationException(f"Unsupported operator type: {type(node.value)}")

    def __cell_name_to_location(self, cell_name: str) -> (int, int):
        """
        Convert a cell name (like 'A1', 'B2', etc.) to its corresponding row and column indices.
        :raises EvaluationException: If the cell name does not match the regular expression.
        :return: A tuple of a row index followed by a column index.
        """
        match = self.__cell_name_pattern.match(cell_name)
        if not match:
            raise EvaluationException(f"Invalid cell name format: {cell_name}")
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
        # TODO - check this running main with a larger sheet.
        name = ""
        while col_index >= 0:
            name += chr(col_index % cls.__NUMBER_OF_LETTERS + cls.__A_ASCII)
            col_index = col_index // cls.__NUMBER_OF_LETTERS - 1
        return name
