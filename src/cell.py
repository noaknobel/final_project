from typing import Union

from data_type import DataType


class Cell:
    def __init__(self, value, data_type):
        self.__value: Union[str, int, float] = value
        self.__data_type: DataType = data_type

    def get_value(self) -> Union[str, int, float]:
        return self.__value

    def update(self, value, data_type: DataType):
        self.__value = value
        self.__data_type = data_type
