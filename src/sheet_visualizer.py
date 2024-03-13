import tkinter as tk
from src.sheet import Sheet

class SheetVisualizer:
    def __init__(self, sheet):
        self.sheet: Sheet = sheet
        self.root = tk.Tk()
        self.root.title("Sheet Visualizer")
        self.cells = {}
        self.current_cell = None
        self.current_cell_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.current_cell_label.grid(row=1, column=1, columnspan=self.sheet.columns_num+1)
        self.create_sheet_ui()

    def create_sheet_ui(self):
        # Add title row
        title_label = tk.Label(self.root, text="Noa's Spreadsheet", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=1, columnspan=self.sheet.columns_num+1, pady=10)

        # Add current cell indicator row
        current_cell_row = 1

        # Add index row (row numbers)
        for row in range(1, self.sheet.rows_num + 1):
            index_label = tk.Label(self.root, text=str(row), font=("Arial", 14))
            index_label.grid(row=row + 2, column=0)

        # Add Excel-like column labels
        for col in range(1, self.sheet.columns_num + 1):
            col_label = tk.Label(self.root, text=chr(col + 64), font=("Arial", 14))
            col_label.grid(row=2, column=col + 1)

        # Add cells
        for row in range(1, self.sheet.rows_num + 1):
            for col in range(1, self.sheet.columns_num + 1):
                cell_value = self.sheet.get_cell(row, col).value
                cell_entry = tk.Entry(self.root, width=10, font=("Arial", 14))
                cell_visual = str(cell_value) if cell_value is not None else ""
                cell_entry.insert(tk.END, cell_visual)
                cell_entry.grid(row=row + 2, column=col + 1)
                self.cells[(row, col)] = cell_entry
                cell_entry.bind("<FocusIn>", lambda event, r=row, c=col: self.update_current_cell_label(r, c))
                cell_entry.bind("<FocusOut>", self.clear_current_cell_label)
                cell_entry.bind("<Escape>", self.reset_current_cell)

        save_button = tk.Button(self.root, text="Save", command=self.save_sheet)
        save_button.grid(row=self.sheet.rows_num + 3, column=self.sheet.columns_num // 2 + 1, pady=10)

    def update_current_cell_label(self, row, col):
        cell_name = f"{chr(64 + col)}{row}"
        self.current_cell_label.config(text=f"Current Cell: {cell_name}")
        self.current_cell = (row, col)

    def clear_current_cell_label(self, event):
        self.current_cell_label.config(text="")
        self.current_cell = None

    def reset_current_cell(self, event):
        self.root.focus_set()  # Remove focus from the entry widget
        self.current_cell = None
        self.current_cell_label.config(text="")

    def save_sheet(self):
        for (row, col), cell_entry in self.cells.items():
            value = cell_entry.get()
            self.sheet.set_cell(row, col, value)
        print("Sheet saved successfully!")

    def run(self):
        self.root.mainloop()
