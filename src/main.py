from sheet import Sheet
from sheet_visualizer import SheetVisualizer


def main():
    my_sheet = Sheet(rows=20, columns=10)
    my_visualizer = SheetVisualizer(my_sheet)
    my_visualizer.run()


if __name__ == '__main__':
    main()
