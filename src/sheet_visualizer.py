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
        for row in range(1, self.sheet.rows_num + 1):
            for col in range(1, self.sheet.columns_num + 1):
                cell_value = self.sheet.get_cell(row, col).value
                cell_entry = tk.Entry(self.root, width=10)
                cell_visual: str = str(cell_value) if cell_value is not None else ""
                cell_entry.insert(tk.END, cell_visual)  # Ensure the cell_value is converted to string
                cell_entry.grid(row=row, column=col)
                self.cells[(row, col)] = cell_entry

        save_button = tk.Button(self.root, text="Save", command=self.save_sheet)
        save_button.grid(row=self.sheet.rows_num + 1, column=self.sheet.columns_num // 2)

    def save_sheet(self):
        for (row, col), cell_entry in self.cells.items():
            value = cell_entry.get()
            self.sheet.set_cell(row, col, value)
        print("Sheet saved successfully!")

    def run(self):
        self.root.mainloop()
