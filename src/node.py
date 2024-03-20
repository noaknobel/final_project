from typing import Any, List, Optional, Union

from math_operator import MathOperator


class Node:
    def __init__(self, value: Union[MathOperator, float, str], left: Optional["Node"] = None, right: Optional["Node"] = None) -> None:
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

    # TODO - consider remove all traversal methods (if not used).

    def __preorder(self, root: "Node", result: List) -> None:
        if not root:
            return
        result.append(root.value)
        self.__preorder(root.left, result)
        self.__preorder(root.right, result)

    def __inorder(self, root: "Node", result: List) -> None:
        if not root:
            return
        self.__inorder(root.left, result)
        result.append(root.value)
        self.__inorder(root.right, result)

    def __postorder(self, root: "Node", result: List) -> None:
        if not root:
            return
        self.__postorder(root.left, result)
        self.__postorder(root.right, result)
        result.append(root.value)

    def preorder(self) -> List["Node"]:
        result = []
        self.__preorder(self, result)
        return result

    def inorder(self) -> List["Node"]:
        result = []
        self.__inorder(self, result)
        return result

    def postorder(self) -> List["Node"]:
        result = []
        self.__postorder(self, result)
        return result
