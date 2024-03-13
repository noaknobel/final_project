import tkinter as tk

from src.sheet import Sheet


class SheetVisualizer:
    def __init__(self, sheet):
        self.sheet: Sheet = sheet
        self.root = tk.Tk()
        self.root.title("Sheet Visualizer")
        self.cells = {}

        self.create_sheet_ui()

    def create_sheet_ui(self):
        # Add title row
        title_label = tk.Label(self.root, text="Noa's Spreadsheet", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=1, columnspan=self.sheet.columns_num+1, pady=10)

        # Add index row (row numbers)
        for row in range(1, self.sheet.rows_num + 1):
            index_label = tk.Label(self.root, text=str(row), font=("Arial", 14))
            index_label.grid(row=row + 1, column=0)

        # Add Excel-like column labels
        for col in range(1, self.sheet.columns_num + 1):
            col_label = tk.Label(self.root, text=chr(col + 64), font=("Arial", 14))
            col_label.grid(row=1, column=col + 1)

        # Add cells
        for row in range(1, self.sheet.rows_num + 1):
            for col in range(1, self.sheet.columns_num + 1):
                cell_value = self.sheet.get_cell(row, col).value
                cell_entry = tk.Entry(self.root, width=10, font=("Arial", 14))
                cell_visual = str(cell_value) if cell_value is not None else ""
                cell_entry.insert(tk.END, cell_visual)
                cell_entry.grid(row=row + 1, column=col + 1)
                self.cells[(row, col)] = cell_entry

        save_button = tk.Button(self.root, text="Save", command=self.save_sheet)
        save_button.grid(row=self.sheet.rows_num + 2, column=self.sheet.columns_num // 2 + 1, pady=10)

    def save_sheet(self):
        for (row, col), cell_entry in self.cells.items():
            value = cell_entry.get()
            self.sheet.set_cell(row, col, value)
        print("Sheet saved successfully!")

    def run(self):
        self.root.mainloop()
