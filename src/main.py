from sheet import Sheet
from sheet_visualizer import SheetVisualizer


def main():
    my_sheet = Sheet(rows_number=20, columns_number=10)
    my_visualizer = SheetVisualizer(my_sheet)
    my_visualizer.run()


if __name__ == '__main__':
    main()
