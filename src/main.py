from src.sheet import Sheet
from src.sheet_visualizer import SheetVisualizer


def main():
    my_sheet = Sheet(rows=5, columns=5)
    my_visualizer = SheetVisualizer(my_sheet)
    my_visualizer.run()


if __name__ == '__main__':
    main()
