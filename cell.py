from typing import Union

from node import Node


class Cell:
    """
    This class serves as a container for values relevant for a specific cell in a sheet.
    """

    def __init__(self, cell_content: str, parsed_content: Union[str, float, Node]):
        """
        Initializes the Cell with raw and parsed content.
        :param cell_content: The raw string content of the cell.
        :param parsed_content: The content of the cell that has been parsed into a str, float, or Node.
        """
        self.__content: str = cell_content
        self.__parsed_content: Union[str, float, Node] = parsed_content

    def get_content(self) -> str:
        """
        Returns the raw string content that is stored in the cell.
        """
        return self.__content

    def get_parsed_content(self) -> Union[str, float, Node]:
        """
        Returns the parsed content of the cell.
        """
        return self.__parsed_content
