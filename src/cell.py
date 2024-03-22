from typing import Union

from node import Node


class Cell:
    def __init__(self, cell_content: str, parsed_content: Union[str, float, Node]):
        self.__content: str = cell_content
        self.__parsed_content: Union[str, float, Node] = parsed_content

    def get_content(self) -> str:
        """
        Returns the raw string content that is stored in the cell.
        """
        return self.__content

    def get_parsed_content(self) -> Union[str, float, Node]:
        return self.__parsed_content
