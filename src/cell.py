from typing import Union


class Cell:
    def __init__(self, value=None):
        self.value: Union[str, int, float] = value

