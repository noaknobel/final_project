from typing import Dict, Tuple, Union, Optional

from cell import Cell
from data_type import DataType

# TODO - place in a place for all classes.
Numeric = Union[float, int]
Value = Union[Numeric, str]
Location = Tuple[int, str]


class Sheet:
    def __init__(self, rows_number: int, columns_number: int):
        self.__rows_num: int = rows_number
        self.__columns_num: int = columns_number
        self.__cells: Dict[Location, Cell] = {}  # Dictionary to store cells with their coordinates

    def get_rows_number(self) -> int:
        return self.__rows_num

    def get_columns_number(self) -> int:
        return self.__columns_num

    def get_cell(self, row, column) -> Optional[Cell]:
        cell: Optional[Cell] = self.__cells.get((row, column))
        if cell is None:
            return None
        return cell.get_value()

    def try_update(self, cell_location: Location, value: Value) -> Tuple[bool, Dict[Location, Value]]:
        # TODO if formula - handle + handle exceptions.
        value, data_type = self.__parse_value(value)
        if cell_location in self.__cells:
            self.__cells[cell_location].update(value, data_type)
        else:
            self.__cells[cell_location] = Cell(value, data_type)
        updated_cells = {cell_location: self.__cells[cell_location].get_value()}
        print({k: v.get_value() for k, v in self.__cells.items()})  # todo - remove
        return True, updated_cells

    def __parse_value(self, value: str) -> Tuple[Value, DataType]:
        if self.__is_number(value):
            return float(value), DataType.NUMBER
        if self.__is_formula(value):
            pass
            return  # TODO
        return value, DataType.STRING

    @staticmethod
    def __is_number(value: str) -> bool:
        # TODO - this code already exists in the parser.
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def __is_formula(value: str) -> bool:
        return value.startswith("=")
