from typing import Optional, Union, Generator

from math_operator import MathOperator


class Node:
    """
    Represents a node in a binary tree, holding a value and references to left and right child nodes.

    The value of the node can be a MathOperator, float, or str, making this class versatile for
    representing expressions or other hierarchical data structures.

    Attributes:
        value (Union[MathOperator, float, str]): The value held by the node.
        left (Optional[Node]): A reference to the left child Node.
        right (Optional[Node]): A reference to the right child Node.
    """
    def __init__(self, value: Union[MathOperator, float, str], left: Optional["Node"] = None,
                 right: Optional["Node"] = None) -> None:
        self.value: Union[MathOperator, float, str] = value
        self.left: Node = left
        self.right: Node = right

    def __str__(self) -> str:
        """Returns a human-readable string representation of the Node."""
        value = self.value.symbol if isinstance(self.value, MathOperator) else self.value
        return f"Node: (value: {value}, left: {self.left}, right: {self.right})"

    def __repr__(self) -> str:
        """Returns an unambiguous string representation of the Node, useful for debugging."""
        return f"Node(value={self.value}, left={self.left}, right={self.right})"

    def is_leaf(self) -> bool:
        """
        Determines if the node is a leaf (i.e., has no children).

        :return: True if the node has no left or right child, False otherwise.
        """
        return self.left is None and self.right is None

    def preorder(self) -> Generator["Node", None, None]:
        """
        Generates the nodes in a preorder traversal starting from this node.

        Yields the current node, then recursively yields from the left and right
        children (if they exist), providing a way to iterate through the tree nodes
        in preorder.

        :return: A generator yielding Node instances in preorder.
        """
        yield self  # Yield the current node
        if self.left is not None:
            yield from self.left.preorder()  # Recursively yield from left subtree
        if self.right is not None:
            yield from self.right.preorder()  # Recursively yield from right subtree
