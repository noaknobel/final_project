import argparse
from json import JSONDecodeError

from exceptions import SheetLoadException, BadNameException, ParserException, CircularDependenciesException
from sheet import Sheet
from sheet_visualizer import SheetVisualizer


def main():
    try:
        parser = argparse.ArgumentParser(description="Guidance for Utilizing Noa's Spreadsheet\n\n"
                                                     "While the user interface of Noa's Spreadsheet is designed to be"
                                                     " highly intuitive, we offer the following tips to ensure you"
                                                     " maximize your experience:\n"
                                                     "1. Inserting Formulas: Initiate a formula by typing '=' followed "
                                                     "by the desired formula expression.\n "
                                                     "The Spreadsheet supports complex formulae that can incorporate "
                                                     "both range functions and mathematical operations.\n"
                                                     "2. Using Built-in Functions: Please ensure that all built-in "
                                                     "function names are entered in lowercase to guarantee "
                                                     "proper function recognition and execution.\n"
                                                     "3. Specifying Ranges: For range functions, employ the ':'"
                                                     " separator to define the range.\n For example, to calculate "
                                                     "the maximum value within a range from cell A1 to A3, you would"
                                                     " use the syntax `max(A1:A3)`.\n"
                                                     "4. Exporting Files: To export your data, enter the desired "
                                                     "filename along with the appropriate file extension, and then "
                                                     "click the 'Save' button to complete the export process.\n\n"
                                                     "By following these guidelines, you can effectively leverage Noa's"
                                                     " Spreadsheet to its fullest potential.",
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
