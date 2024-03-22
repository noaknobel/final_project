import re
from typing import Dict, Tuple, Union, Optional

from cell import Cell
from math_operator import Plus, Minus, Times, Divide, Negate, Sin, Power, MathOperator, UnaryOperator, BinaryOperator
from node import Node
from expression_parser import ExpressionParser

Position = Tuple[int, int]  # (Row Index, Column Index)


class Sheet:
    __EQUATION_PREFIX = "="

    def __init__(self, rows_number: int, columns_number: int):
        self.__rows_num: int = rows_number
        self.__columns_num: int = columns_number
        self.__cells: Dict[Position, Cell] = {}  # Dictionary to store cells with their coordinates
        self.__parser = ExpressionParser(math_operators=[Plus(), Minus(), Times(), Divide(), Negate(), Sin(), Power()],
                                         var_pattern=re.compile(r'^[A-Z]+[0-9]+$'))

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

    def evaluate_position(self, row_index: int, column_index: int) -> Union[str, float]:
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

    @classmethod
    def __evaluate(cls, node: Optional[Node]) -> float:
        """
        Recursively evaluates the syntax tree from the given node.
        :param node: Root of the syntax tree to evaluate.
        :return: Evaluated result as a float.
        :raises ParserException: If the provided node is None or if evaluation fails due to invalid structure.
        """
        if node is None:
            raise Exception("Empty expression.")
        if node.is_leaf():
            return cls.__evaluate_leaf_node(node)
        return cls.__evaluate_internal_node(node)

    @classmethod
    def __evaluate_leaf_node(cls, node: Node) -> float:
        """
        Evaluates a leaf node.
        :param node: The leaf node to evaluate.
        :return: The numerical value associated with the leaf node.
        :raises ParserException: If the leaf node contains an invalid value.
        """
        if isinstance(node.value, float):
            return node.value
        elif isinstance(node.value, str):
            return cls.__get_cell_value(node.value)
        else:
            raise Exception(f"Invalid leaf value: {node.value}")

    @classmethod
    def __evaluate_internal_node(cls, node: Node) -> float:
        """
        Evaluates an internal (non-leaf) node.
        :param node: The internal node to evaluate.
        :return: The result of evaluating the operation represented by the node.
        :raises ParserException: If the node contains an unsupported value or operation.
        """
        if not isinstance(node.value, MathOperator):
            raise Exception(f"Unsupported node value: {node.value}")
        left_val = cls.__evaluate(node.left) if node.left else None
        right_val = cls.__evaluate(node.right) if node.right else None
        if isinstance(node.value, UnaryOperator):
            if right_val is None:
                raise Exception("Missing operand for unary operator.")
            return node.value.calculate(right_val)
        elif isinstance(node.value, BinaryOperator):
            if left_val is None or right_val is None:
                raise Exception("Missing operands for binary operator.")
            return node.value.calculate(left_val, right_val)
        else:
            raise Exception(f"Unsupported operator type: {type(node.value)}")

    @classmethod
    def __get_cell_value(cls, cell_location: str) -> float:
        return float(2)  # TODO
