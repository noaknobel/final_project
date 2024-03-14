from typing import Dict, Tuple, Union, List

from cell import Cell

Numeric = Union[float, int]
Value = Union[Numeric, str]
Location = Tuple[int, str]


class Sheet:
    def __init__(self, rows: int, columns: int):
        self.rows_num: int = rows
        self.columns_num: int = columns
        self.cells: Dict[Location, Cell] = {}  # Dictionary to store cells with their coordinates

    def get_cell(self, row, column):
        return self.cells.get((row, column), Cell())

    def set_cell(self, row, column, value):
        self.cells[(row, column)] = Cell(value)

    def delete_cell(self, row, column):
        del self.cells[(row, column)]

    def try_update(self, current_cell: Location, value: Value) -> Tuple[bool, List[Cell]]:
        # TODO if formula - handle + handle exceptions.
        self.cells[current_cell] = Cell(value)
        updated_cells = [self.cells[current_cell]]
        print(self.cells[current_cell].value)
        return True, updated_cells
