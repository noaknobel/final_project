from typing import Dict, Tuple

from src.cell import Cell


class Sheet:
    def __init__(self, rows, columns):
        self.rows_num: int = rows
        self.columns_num: int = columns
        self.cells: Dict[Tuple[int, int], Cell] = {}  # Dictionary to store cells with their coordinates

    def get_cell(self, row, column):
        return self.cells.get((row, column), Cell())

    def set_cell(self, row, column, value):
        self.cells[(row, column)] = Cell(value)

    def delete_cell(self, row, column):
        del self.cells[(row, column)]
