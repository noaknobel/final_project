import argparse
from json import JSONDecodeError

from exceptions import SheetLoadException, BadNameException, ParserException, CircularDependenciesException
from sheet import Sheet
from sheet_visualizer import SheetVisualizer


def main():
    """
    Initializes the spreadsheet application, processes command-line arguments,
    and manages the main execution flow, including data loading and visualizing the spreadsheet.

    Handles errors related to file operations, data parsing, and spreadsheet logic,
    providing user-friendly messages for each known exception type.
    """
    try:
        parser = argparse.ArgumentParser(description=
                                         "Guidance for Utilizing Noa's Spreadsheet\n\n"
                                         "While the user interface of Noa's Spreadsheet is designed to be highly "
                                         "intuitive,\nwe offer the following tips to ensure you maximize your "
                                         "experience:\n\n"
                                         "1. Inserting Formulas: Initiate by typing '=' followed by the formula.\n "
                                         "The system supports complex formulas, including range functions and "
                                         "operations.\n"
                                         "2. Using Built-in Functions: Ensure all built-in function names are entered "
                                         "in lowercase to guarantee proper function recognition and execution.\n "
                                         "Available operations include:\n"
                                         "   - Arithmetic: '+' (Plus), '-' (Minus), '*' (Times), '/' (Divide)\n"
                                         "   - Functions: 'sin' (Sin), 'power', 'max', 'min', 'sum', 'average'\n"
                                         "   - Special: '-' to negate values\n"
                                         "3. Specifying Ranges: Define ranges within a single column (e.g., 'A1:A4')"
                                         " or a single row (e.g., 'B1:B3'),\n in ascending order and within the sheet's"
                                         " dimensions.\n"
                                         "4. Exporting Files: Choose options for exporting in either CSV or JSON format"
                                         ". Enter the filename and extension, then click 'Save'.\n"
                                         "5. Upload JSON File: Upload data from a JSON file using the command line flag"
                                         " '--json-file' followed by the file path.\nThe program provides an example "
                                         "of a JSON file to illustrate the expected format and structure of the data.\n"
                                         "6. Running the Program: Execute the program from the command line with"
                                         " 'python main.py'.\n\n"
                                         "Adhering to these guidelines will help you leverage Noa's Spreadsheet to its"
                                         " fullest potential.",
                                         formatter_class=argparse.RawTextHelpFormatter)
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
