from enum import Enum, auto
from typing import Union

from node import Node


class ErrorType(Enum):
    VALUE_ERROR = auto()
    NAME_ERROR = auto()


class Cell:
    """
    This class serves as a container for values relevant for a specific cell in a sheet.
    """

    def __init__(self, cell_content: str, parsed_content: Union[str, float, Node], value: Union[str, float, ErrorType]):
        self.__content: str = cell_content
        self.__parsed_content: Union[str, float, Node] = parsed_content
        self.__value: Union[str, float, ErrorType] = value

    def get_content(self) -> str:
        """
        Returns the raw string content that is stored in the cell.
        """
        return self.__content

    def get_parsed_content(self) -> Union[str, float, Node]:
        return self.__parsed_content

    def get_value(self) -> Union[str, float, ErrorType]:
        return self.__value

    def update_value(self, new_value: Union[str, float, ErrorType]):
        self.__value: Union[str, float, ErrorType] = new_value
