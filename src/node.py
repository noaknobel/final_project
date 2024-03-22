from typing import Optional, Union

from math_operator import MathOperator


class Node:
    def __init__(self, value: Union[MathOperator, float, str], left: Optional["Node"] = None,
                 right: Optional["Node"] = None) -> None:
        self.value = value
        self.left = left
        self.right = right

    def __str__(self) -> str:
        value = self.value.symbol if isinstance(self.value, MathOperator) else self.value
        return f"Node: (value: {value}, left: {self.left}, right: {self.right})"

    def __repr__(self) -> str:
        return f"Node(value={self.value}, left={self.left}, right={self.right})"

    def is_leaf(self) -> bool:
        """
        Checks whether the node is a leaf node.
        :return: True if the node is a leaf, False otherwise.
        """
        return self.left is None and self.right is None
