import tkinter as tk
from tkinter import messagebox
from typing import Optional, List, Dict

from failure_reason import FailureReason
from sheet import Sheet, Value


class SheetVisualizer:
    """
    Provides a graphical user interface for interacting with a Sheet instance.
    Allows users to view, modify, and save spreadsheet data through a Tkinter-based GUI.

    Attributes:
        __sheet (Sheet): The Sheet instance being visualized and interacted with.
        __root (tk.Tk): The root Tkinter window for the GUI.
        __current_cell_label (tk.Label): Label displaying the currently selected cell.
        __current_value_label (tk.Label): Label displaying the current value of the selected cell.
        __sheet_entries (List[List[tk.Entry]]): A matrix of Tkinter Entry widgets representing the spreadsheet cells.
    """
    __SPREADSHEET_TITLE = "Sheet Visualizer"
    __SPREADSHEET_NAME = "Noa's Spreadsheet"
    __USER_NAME_LABEL = "Sheet Name:"
    __SAVE_BUTTON_TEXT = "Save"
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
    # Initializing mapping from error types to GUI strings as a dict.
    # Note that a name error probably won't happen in practice since this case should fail during parsing.
    __FAILURE_REASON_STRINGS: Dict[FailureReason, str] = {
        FailureReason.COULD_NOT_PARSE: "Could Not Parse.",
        FailureReason.DEPENDENCIES_CYCLE: "Dependency Cycle Detected.",
        FailureReason.EVALUATION_FAILURE: "Failed to evaluate cell.",
        FailureReason.BAD_NAME_REFERENCE: "Formula contained an invalid name.",
        FailureReason.ZERO_DIVISION: "Cannot divide by zero.",
        FailureReason.UNEXPECTED_EXCEPTION: "Aborted - Unexpected Exception."
    }

    def __init__(self, sheet):
        """
        Initializes the SheetVisualizer with a given Sheet instance, setting up the GUI elements.

        :param sheet: The Sheet instance to visualize and interact with.
        """
        self.__sheet: Sheet = sheet
        # Init root tk object.
        self.__root = tk.Tk()
        # Init current cell view.
        self.__current_cell_label = tk.Label(self.__root, text=self.__CURRENT_CELL_DEFAULT_STRING, font=self.__FONT)
        self.__current_value_label = tk.Label(self.__root, text=self.__CURRENT_CELL_DEFAULT_STRING, font=self.__FONT)
        # Generate the grid of cells.
        self.__create_sheet_ui()

    def run(self):
        """
        Starts the Tkinter main loop, displaying the GUI and allowing user interaction.
        """
        self.__root.mainloop()

    def __create_sheet_ui(self) -> None:
        """
        Sets up the initial GUI layout, including the spreadsheet header and cell grid.
        """
        self.__root.title(self.__SPREADSHEET_TITLE)  # Set the title in the upper left corner of the view.
        self.__add_gui_sheet_header()
        self.__add_gui_table_indexes()
        self.__add_gui_sheet_table_cells()

    def __add_gui_table_indexes(self) -> None:
        """
        Adds indexes of columns and rows to the gui.
        """
        # Add Excel-like column labels.
        for col_index in range(self.__sheet.COLUMNS_NUM):
            col_label = tk.Label(self.__root, text=self.__sheet.column_index_to_name(col_index), font=self.__FONT,
                                 fg=self.__COLOR)
            col_label.grid(row=self.__COLUMN_NAMES_ROW, column=col_index + self.__FIRST_COLUMN_NAME_INDEX)
        # Add column of row indexes.
        for row_index in range(self.__sheet.ROWS_NUM):
            row_name = self.__sheet.row_index_to_name(row_index)  # Row numbers start with 1.
            index_label = tk.Label(self.__root, text=str(row_name), font=self.__FONT, fg=self.__COLOR)
            index_label.grid(row=row_index + self.__FIRST_SPREADSHEET_ROW, column=self.__ROW_INDEX_COLUMN)

    def __add_gui_sheet_header(self) -> None:
        """
        Adds the spreadsheet's header elements to the GUI, including the title and save button.
        """
        # Add title
        title_label = tk.Label(self.__root, text=self.__SPREADSHEET_NAME, font=self.__TITLE_FONT, fg=self.__TITLE_COLOR)
        title_label.grid(row=self.__SPREADSHEET_NAME_ROW, column=1, columnspan=self.__sheet.COLUMNS_NUM + 2, pady=10)
        # Add a save button
        save_button = tk.Button(self.__root, text=self.__SAVE_BUTTON_TEXT, command=self.__save_changes)
        save_button.grid(row=self.__SPREADSHEET_NAME_ROW, column=1, pady=5, sticky="w")
        column_span_length = self.__sheet.COLUMNS_NUM + 1
        # Add label "Sheet name:"
        sheet_name_label = tk.Label(self.__root, text=self.__USER_NAME_LABEL, font=self.__FONT)
        sheet_name_label.grid(row=self.__SPREADSHEET_USER_NAME_ROW, column=1, pady=5, sticky="e")
        # Add entry widget for title
        self.__smaller_title_entry = tk.Entry(self.__root, font=self.__FONT)
        self.__smaller_title_entry.grid(row=self.__SPREADSHEET_USER_NAME_ROW, column=2, columnspan=column_span_length,
                                        pady=5, sticky="w")
        # Place the current cell & value in the visual grid.
        self.__current_cell_label.grid(row=self.__CURRENT_CELL_ROW, column=1, columnspan=column_span_length)
        self.__current_value_label.grid(row=self.__CURRENT_CELL_VALUE_ROW, column=1, columnspan=column_span_length)

    def __save_changes(self) -> None:
        # Retrieve the file name from the entry widget
        file_name = self.__smaller_title_entry.get()
        if not file_name:  # Check if the file name is not empty
            messagebox.showwarning("Warning", "Please enter a file name.")
            return

        # Use the file name to save the sheet
        save_success = self.__sheet.try_save(file_name)
        if save_success:
            messagebox.showinfo("Save Successful", "The changes were successfully saved.")
        else:
            messagebox.showerror("Save Failed", "Failed to store the changes.")

    def __add_gui_sheet_table_cells(self) -> None:
        """
        Adds the sheet matrix to the GUI.
        Initializes the matrix of entries, enters the current state values to the view,
        and bind each entry to GUI events.
        """
        self.__sheet_entries: List[List[tk.Entry]] = [
            [tk.Entry(self.__root, width=10, font=self.__FONT) for _ in range(self.__sheet.COLUMNS_NUM)]
            for _ in range(self.__sheet.ROWS_NUM)
        ]
        for row_index, entries_row in enumerate(self.__sheet_entries):
            for col_index, entry in enumerate(entries_row):
                value: Optional[Value] = self.__sheet.get_value(row_index, col_index)
                entry.insert(tk.END, self.__value_to_show(value))
                self.__bind_entry_events(entry, row_index, col_index)
                # Add the entry to the table view.
                entry.grid(row=row_index + self.__FIRST_SPREADSHEET_ROW,
                           column=col_index + self.__FIRST_COLUMN_NAME_INDEX)

    def __bind_entry_events(self, entry: tk.Entry, row_index: int, col_index: int):
        """
        Binds specific callback methods to entry widget events, managing GUI interactions based on user input.
        """
        entry.bind("<FocusIn>", lambda event, r=row_index, c=col_index: self.__focus_in_entry(entry, r, c))
        entry.bind("<KeyRelease>", lambda event, r=row_index, c=col_index: self.__key_write_entry(entry))
        entry.bind("<FocusOut>", lambda event, r=row_index, c=col_index: self.__focus_out_cell(entry, r, c))

    def __focus_in_entry(self, entry: tk.Entry, row_index: int, col_index: int):
        """
        Gets stored string in the given position and updates the view,
        in the current cell header view and in the entry content.
        The method occurs when the user clicks on the bound entry.
        """
        self.__current_cell_label.config(text=f"Cell: {self.__sheet.get_cell_name(col_index, row_index)}")
        content: Optional[str] = self.__sheet.get_cell_content(row_index, col_index)
        self.__update_entry_text(entry, content)
        if content is not None:
            self.__update_current_cell_text_view(content)

    @staticmethod
    def __update_entry_text(entry: tk.Entry, content: Optional[str]):
        """Update the view of the cell itself."""
        entry.delete(0, tk.END)
        entry.insert(0, "" if content is None else content)

    def __key_write_entry(self, entry: tk.Entry):
        """
        Updates the key write that updated the entry to the current-cell view.
        When this method runs, the entry has focus-in, so it shows the content and not the evaluation of the cell.
        Therefore, getting the current content of the entry while typing, should always provide the raw text content.
        """
        self.__update_current_cell_text_view(entry.get())

    def __update_current_cell_text_view(self, content):
        """Update the label of the current cell content in the head of the view."""
        self.__current_value_label.config(text=f"Content: {content}")

    def __focus_out_cell(self, entry: tk.Entry, row_index: int, col_index: int):
        """Callback when focus out of entry cell."""
        self.__clear_current_cell_header_view()
        self.__store_and_evaluate_cell(entry, row_index, col_index)

    def __clear_current_cell_header_view(self):
        """A method that clears the labels of the current cell in the header."""
        self.__current_cell_label.config(text=self.__CURRENT_CELL_DEFAULT_STRING)
        self.__current_value_label.config(text=self.__CURRENT_CELL_DEFAULT_STRING)

    def __store_and_evaluate_cell(self, entry: tk.Entry, row_index: int, col_index: int):
        """
        The method assumes row_index, col_index are valid indexes in the sheet.
        """
        written_content: str = entry.get()
        success, positions_to_values, failure_reason = self.__sheet.try_update(row_index, col_index, written_content)
        if success:
            for (row_index, col_index), value in positions_to_values.items():
                entry = self.__sheet_entries[row_index][col_index]
                self.__update_entry_text(entry, self.__value_to_show(value))
        else:
            old_value = self.__sheet.get_value(row_index, col_index)
            self.__update_entry_text(entry, self.__value_to_show(old_value))
            self.__show_failure_reason_message_box(failure_reason)

    @staticmethod
    def __value_to_show(value: Optional[Value]) -> Optional[str]:
        """Give a value in a sheet cell, return the string value that should be shown in the GUI."""
        return "" if value is None else str(value)

    @classmethod
    def __show_failure_reason_message_box(cls, failure_reason: FailureReason) -> None:
        """Pop an error message box on the screen with the relevant error message to the given failure reason."""
        error_message = cls.__FAILURE_REASON_STRINGS.get(failure_reason, "An unknown error occurred.")
        # Display the error message in a popup message box.
        messagebox.showerror("Error", error_message)
