import argparse
from json import JSONDecodeError

from exceptions import SheetLoadException, BadNameException, ParserException, CircularDependenciesException
from sheet import Sheet
from sheet_visualizer import SheetVisualizer


def main():
    try:
        parser = argparse.ArgumentParser(description="Noa's spreadsheet.")
        parser.add_argument("--json-file", type=str, default=None, help="Path to the JSON file")
        args = parser.parse_args()
        json_file: str = args.json_file
        my_sheet = Sheet(json_file) if json_file else Sheet()
        my_visualizer = SheetVisualizer(my_sheet)
        my_visualizer.run()
    except FileNotFoundError:
        print("Please provide an existing file.")
    except (JSONDecodeError, PermissionError, TypeError) as e:
        print(f"Failed while loading json file: {str(e)}")
    except (SheetLoadException, ParserException) as e:
        print(f"Json file data cannot be loaded as a valid sheet: {e}")
    except CircularDependenciesException as e:
        print(f"A failure due to dependency cycle in the data: {e}")
    except BadNameException as e:
        print(f"Json file Contained an invalid cell name.")
    except Exception as e:
        print(f"There was an unexpected error in the program: {str(e)}")


if __name__ == '__main__':
    main()
