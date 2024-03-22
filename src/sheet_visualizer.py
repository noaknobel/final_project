import tkinter as tk
from typing import Optional, List

# TODO - think how to remove direct access to cell here, and use it only through sheet's api,
#  or - separate the visual cell class from evaltion and logic class.
from cell import Cell
from sheet import Sheet


class SheetVisualizer:
    __SPREADSHEET_TITLE = "Sheet Visualizer"
    __SPREADSHEET_NAME = "Noa's Spreadsheet"
    __USER_NAME_LABEL = "Sheet Name:"
    __CURRENT_CELL_DEFAULT_STRING = ""
    __FONT = ("Arial", 14)
    __COLOR = "#C8A2C8"
    __TITLE_FONT = ("Arial", 16, "bold")
    __TITLE_COLOR = "#FF69B4"
    # Index numbers of each visual row in the grid header.
    __SPREADSHEET_NAME_ROW = 0
    __SPREADSHEET_USER_NAME_ROW = 1
    __CURRENT_CELL_ROW = 2
    __CURRENT_CELL_VALUE_ROW = 3
    __COLUMN_NAMES_ROW = 4
    __FIRST_SPREADSHEET_ROW = 5
    # Column indexes.
    __ROW_INDEX_COLUMN = 0
    __FIRST_COLUMN_NAME_INDEX = 1
    # Column names consts.
    __NUMBER_OF_LETTERS = 26
    __A_ASCII = 65

    def __init__(self, sheet):
        self.sheet: Sheet = sheet
        # Init root tk object.
        self.root = tk.Tk()
        # Init current cell view.
        self.current_cell_label = tk.Label(self.root, text=self.__CURRENT_CELL_DEFAULT_STRING, font=self.__FONT)
        self.current_value_label = tk.Label(self.root, text=self.__CURRENT_CELL_DEFAULT_STRING, font=self.__FONT)
        # Generate the grid of cells.
        self.__create_sheet_ui()

    def run(self):
        self.root.mainloop()

    def __create_sheet_ui(self) -> None:
        """
        Initialize GUI of sheet.
        """
        self.root.title(self.__SPREADSHEET_TITLE)  # Set the title in the upper left corner of the view.
        self.__add_gui_sheet_header()
        self.__add_gui_table_indexes()
        self.__add_gui_sheet_table_cells()

    def __add_gui_table_indexes(self) -> None:
        """
        Adds indexes of columns and rows to the gui.
        """
        # Add Excel-like column labels.
        for col_index in range(self.sheet.get_columns_number()):
            col_label = tk.Label(self.root, text=self.__column_index_to_name(col_index), font=self.__FONT,
                                 fg=self.__COLOR)
            col_label.grid(row=self.__COLUMN_NAMES_ROW, column=col_index + self.__FIRST_COLUMN_NAME_INDEX)
        # Add column of row indexes.
        for row_index in range(self.sheet.get_rows_number()):
            row_name = self.__row_index_to_name(row_index)  # Row numbers start with 1.
            index_label = tk.Label(self.root, text=str(row_name), font=self.__FONT, fg=self.__COLOR)
            index_label.grid(row=row_index + self.__FIRST_SPREADSHEET_ROW, column=self.__ROW_INDEX_COLUMN)

    def __add_gui_sheet_header(self) -> None:
        """
        Adds GUI header components such as the title, save button, current cell presentation, etc.
        """
        # Add title
        title_label = tk.Label(self.root, text=self.__SPREADSHEET_NAME, font=self.__TITLE_FONT, fg=self.__TITLE_COLOR)
        title_label.grid(row=self.__SPREADSHEET_NAME_ROW, column=1, columnspan=self.sheet.get_columns_number() + 2,
                         pady=10)
        # Add a save button
        save_button = tk.Button(self.root, text="Save", command=self.__save_changes)
        save_button.grid(row=self.__SPREADSHEET_NAME_ROW, column=1, pady=5, sticky="w")
        column_span_length = self.__row_index_to_name(self.sheet.get_columns_number())
        # Add label "Sheet name:"
        sheet_name_label = tk.Label(self.root, text=self.__USER_NAME_LABEL, font=self.__FONT)
        sheet_name_label.grid(row=self.__SPREADSHEET_USER_NAME_ROW, column=1, pady=5, sticky="e")
        # Add entry widget for title
        smaller_title_entry = tk.Entry(self.root, font=self.__FONT)
        smaller_title_entry.grid(row=self.__SPREADSHEET_USER_NAME_ROW, column=2, columnspan=column_span_length, pady=5,
                                 sticky="w")
        # Place the current cell & value in the visual grid.
        self.current_cell_label.grid(row=self.__CURRENT_CELL_ROW, column=1, columnspan=column_span_length)
        self.current_value_label.grid(row=self.__CURRENT_CELL_VALUE_ROW, column=1, columnspan=column_span_length)

    def __save_changes(self):
        # todo: Implement saving logic here
        pass

    def __add_gui_sheet_table_cells(self) -> None:
        """
        Adds the sheet matrix to the GUI.
        Initializes the entries matrix, enters the current state values to the view, and bind each entry to GUI events.
        """
        self.__sheet_entries: List[List[tk.Entry]] = [
            [tk.Entry(self.root, width=10, font=self.__FONT) for _ in range(self.sheet.get_columns_number())]
            for _ in range(self.sheet.get_rows_number())
        ]
        for row_index, entries_row in enumerate(self.__sheet_entries):
            for col_index, entry in enumerate(entries_row):
                cell: Optional[Cell] = self.sheet.get_cell(row_index, col_index)
                entry.insert(tk.END, cell.get_value() if cell is not None else "")  # TODO - check.
                self.__bind_entry_events(entry, row_index, col_index)
                # Add the entry to the table view.
                entry.grid(row=row_index + self.__FIRST_SPREADSHEET_ROW,
                           column=col_index + self.__FIRST_COLUMN_NAME_INDEX)

    @staticmethod
    def __row_index_to_name(row_index: int) -> str:
        """
        A string label representing the row, starting with "1" in the 0 index.
        """
        return str(row_index + 1)

    @classmethod
    def __column_index_to_name(cls, col_index: int) -> str:
        """
        A string label representing the column, starting with "A".
        """
        # TODO - check this running main with a larger sheet.
        name = ""
        while col_index >= 0:
            name += chr(col_index % cls.__NUMBER_OF_LETTERS + cls.__A_ASCII)
            col_index = col_index // cls.__NUMBER_OF_LETTERS - 1
        return name

    def __bind_entry_events(self, entry: tk.Entry, row_index: int, col_index: int):
        """
        Binds specific callback methods to entry widget events, managing GUI interactions based on user input.
        """
        entry.bind("<FocusIn>", lambda event, r=row_index, c=col_index: self.__focus_in_entry(entry, r, c))
        entry.bind("<KeyRelease>", lambda event, r=row_index, c=col_index: self.__key_write_entry(entry))
        entry.bind("<FocusOut>", lambda event, r=row_index, c=col_index: self.__focus_out_cell(r, c))

    def __focus_in_entry(self, entry: tk.Entry, row_index: int, col_index: int):
        """
        Gets stored string in the given position and updates the view,
        in the current cell header view and in the entry content.
        The method occurs when the user clicks on the bound entry.
        """
        self.current_cell_label.config(text=f"Cell: {self.__get_cell_name(col_index, row_index)}")
        cell: Optional[Cell] = self.sheet.get_cell(row_index, col_index)
        if cell is not None:
            content: str = cell.get_content()
            # Update the label of the current cell content in the head of the view.
            self.current_value_label.config(text=f"Content: {content}")
            # Update the view of the cell itself.
            entry.delete(0, tk.END)
            entry.insert(0, content)

    def __get_cell_name(self, col_index: int, row_index: int) -> str:
        row_name: int = self.__row_index_to_name(row_index)
        col_name: str = self.__column_index_to_name(col_index)
        return f"{col_name}{row_name}"

    def __key_write_entry(self, entry: tk.Entry):
        """
        Updates the key write that updated the entry to the current-cell view.
        When this method runs, the entry has focus-in, so it shows the content and not the evaluation of the cell.
        Therefore, getting the current content of the entry while typing, should always provide the raw text content.
        """
        self.current_value_label.config(text=f"Content: {entry.get()}")

    def __focus_out_cell(self, row_index: int, col_index: int):
        self.__clear_current_cell_header_view()
        self.__store_and_evaluate_cell(row_index, col_index)

    def __clear_current_cell_header_view(self):
        self.current_cell_label.config(text=self.__CURRENT_CELL_DEFAULT_STRING)
        self.current_value_label.config(text=self.__CURRENT_CELL_DEFAULT_STRING)

    def __store_and_evaluate_cell(self, row_index: int, col_index: int):
        current_cell_val = self.__get_current_cell_value()
        cell: Optional[Cell] = self.sheet.get_cell(row_index, col_index)
        if cell is not None:
            # todo - check the success and update the updated cells in the ui.
            success, locations_to_updated_values = self.sheet.try_update(self.current_cell_position, current_cell_val)
            if success:
                for (row, col), value in locations_to_updated_values.items():
                    entry = self.__sheet_entries[row][col]  # todo - validate loc in range.
                    entry.delete(0, tk.END)
                    entry.insert(0, str(value))
            else:
                pass
                # TODO - handle error
