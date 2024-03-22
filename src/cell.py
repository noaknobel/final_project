from typing import Union


class Cell:
    def __init__(self, cell_content: str):
        self.__content: str = cell_content

    def get_content(self) -> str:
        """
        Returns the raw string content that is stored in the cell.
        """
        return self.__content

    def get_value(self) -> Union[str, float]:
        """
        Computes the value of the cell content and return a float value of the result.
        If the cell content can't be estimated as a float, return the string content itself.
        """
        return self.__content
