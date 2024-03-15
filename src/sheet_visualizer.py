import tkinter as tk
from typing import Optional, Tuple, Union, Dict

from sheet import Sheet


class SheetVisualizer:
    SPREADSHEET_TITLE = "Sheet Visualizer"
    SPREADSHEET_NAME = "Noa's Spreadsheet"
    CURRENT_CELL_DEFAULT_STRING = ""
    FONT = ("Arial", 14)
    TITLE_FONT = ("Arial", 16, "bold")
    # Index numbers of each visual row in the grid header.
    SPREADSHEET_NAME_ROW = 0
    CURRENT_CELL_ROW = 1
    CURRENT_CELL_VALUE_ROW = 2
    COLUMN_NAMES_ROW = 3
    FIRST_SPREADSHEET_ROW = 4
    # Column indexes.
    ROW_INDEX_COLUMN = 0
    FIRST_COLUMN_NAME_INDEX = 1

    def __init__(self, sheet):
        self.sheet: Sheet = sheet

        # Init root tk object.
        self.root = tk.Tk()
        # Store visual entries of cells.
        self.cell_entries: Dict[Tuple[int, str], tk.Entry] = {}  # todo - consider matrix.

        # Init current cell items.
        self.current_cell: Optional[Tuple[int, str]] = None  # Initially the cursor is not on a cell.
        self.current_cell_label = tk.Label(self.root, text=self.CURRENT_CELL_DEFAULT_STRING, font=self.FONT)
        self.current_value_label = tk.Label(self.root, text=self.CURRENT_CELL_DEFAULT_STRING, font=self.FONT)

        # Generate the grid of cells.
        self.__create_sheet_ui()

    def run(self):
        self.root.mainloop()

    def __create_sheet_ui(self):
        # Set the title in the upper left corner of the view.
        # todo: separate to func
        self.root.title(self.SPREADSHEET_TITLE)

        # Add title row
        title_label = tk.Label(self.root, text=self.SPREADSHEET_NAME, font=self.TITLE_FONT)
        title_label.grid(row=self.SPREADSHEET_NAME_ROW, column=1, columnspan=self.sheet.get_columns_number() + 2, pady=10)

        # Place the current cell & value in the visual grid.
        self.current_cell_label.grid(row=self.CURRENT_CELL_ROW, column=1, columnspan=self.sheet.get_columns_number() + 1)
        self.current_value_label.grid(row=self.CURRENT_CELL_VALUE_ROW, column=1, columnspan=self.sheet.get_columns_number() + 1)

        # Add Excel-like column labels.
        for col_index in range(self.sheet.get_columns_number()):
            col_label = tk.Label(self.root, text=self.__get_column_name(col_index), font=self.FONT)
            col_label.grid(row=self.COLUMN_NAMES_ROW, column=col_index + self.FIRST_COLUMN_NAME_INDEX)

        # Add column of row indexes.
        for row_index in range(self.sheet.get_rows_number()):
            row_name = row_index + 1  # Row numbers start with 1.
            index_label = tk.Label(self.root, text=str(row_name), font=self.FONT)
            index_label.grid(row=row_index + self.FIRST_SPREADSHEET_ROW, column=self.ROW_INDEX_COLUMN)

        # Add cells
        self.__add_sheet_ui_to_grid()

    def __add_sheet_ui_to_grid(self):
        # todo - separate func.
        for row_index in range(self.sheet.get_rows_number()):
            row: int = row_index + 1
            for col_index in range(self.sheet.get_columns_number()):
                col: str = self.__get_column_name(col_index)
                cell_value: Union[str, int, float] = self.sheet.get_value(row, col)
                cell_visual = str(cell_value) if cell_value is not None else ""
                cell_entry = tk.Entry(self.root, width=10, font=self.FONT)
                cell_entry.insert(tk.END, cell_visual)
                cell_entry.grid(row=row_index + self.FIRST_SPREADSHEET_ROW, column=col_index + 1)
                # Store the Entry object of each position.
                self.cell_entries[(row, col)] = cell_entry
                # Set callbacks on GUI actions.
                cell_entry.bind("<FocusIn>", lambda event, r=row, c=col: self.__update_current_cell_label(r, c))
                cell_entry.bind("<FocusOut>", self.__clear_current_cell_label)
                cell_entry.bind("<KeyRelease>", self.__update_current_value_label)
                cell_entry.bind("<Return>", self.__update_current_cell_value)
                # TODO - updates Escape behavior and add an Enter action.

    @staticmethod
    def __get_column_name(col_index):
        # TODO - consider moving this to another class.
        return chr(col_index + 65)

    def __update_current_cell_label(self, row: int, col: str):
        cell_name = f"{col}{row}"
        self.current_cell_label.config(text=f"Current Cell: {cell_name}")
        self.current_cell = (row, col)
        self.__update_current_value_label()

    def __clear_current_cell_label(self, event):
        self.current_cell_label.config(text=self.CURRENT_CELL_DEFAULT_STRING)
        self.current_value_label.config(text=self.CURRENT_CELL_DEFAULT_STRING)
        self.__update_current_cell_value()
        self.current_cell = None

    def __get_current_cell_value(self) -> Optional[str]:
        if self.current_cell:
            current_cell_entry = self.cell_entries[self.current_cell]
            return current_cell_entry.get()
        return None

    def __update_current_value_label(self, event=None):
        current_cell_val = self.__get_current_cell_value()
        if current_cell_val is not None:
            self.current_value_label.config(text=f"Cell Content: {current_cell_val}")

    def __update_current_cell_value(self, event=None):
        current_cell_val = self.__get_current_cell_value()
        if current_cell_val is not None:
            # todo - check the success and update the updated cells in the ui.
            success, locations_to_updated_values = self.sheet.try_update(self.current_cell, current_cell_val)
            if success:
                for loc, value in locations_to_updated_values.items():
                    entry = self.cell_entries.get(loc)
                    entry.delete(0, tk.END)
                    entry.insert(0, str(value))
            else:
                pass
                # TODO - handle error
