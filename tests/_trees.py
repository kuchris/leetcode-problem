"""Binary-tree helpers for tests of TreeNode-based solutions."""

import collections

from _loader import load_solution


class TreeNode:
    """Stand-in for the TreeNode that LeetCode injects via its preamble."""

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build(values) -> "TreeNode | None":
    """Build a tree from LeetCode's level-order list.

    ``None`` marks a missing child, and children of a missing node are not
    listed at all (the usual ``[1, null, 2, 3]`` layout).
    """
    if not values:
        return None
    root = TreeNode(values[0])
    queue = collections.deque([root])
    index = 1
    while queue and index < len(values):
        node = queue.popleft()
        for side in ('left', 'right'):
            if index >= len(values):
                return root
            value = values[index]
            index += 1
            if value is not None:
                child = TreeNode(value)
                setattr(node, side, child)
                queue.append(child)
    return root


def serialize(root) -> list:
    """Serialize a tree in LeetCode's level-order format (trailing nulls cut)."""
    if root is None:
        return []
    values = []
    queue = collections.deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            values.append(None)
            continue
        values.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while values and values[-1] is None:
        values.pop()
    return values


def to_structure(root):
    """Nested tuple view of a tree: ``(val, left, right)`` with None children."""
    if root is None:
        return None
    return (root.val, to_structure(root.left), to_structure(root.right))


def from_structure(structure) -> "TreeNode | None":
    """Inverse of :func:`to_structure`."""
    if structure is None:
        return None
    value, left, right = structure
    return TreeNode(value, from_structure(left), from_structure(right))


def nodes(root) -> list:
    """Every node object of a tree in pre-order."""
    if root is None:
        return []
    return [root, *nodes(root.left), *nodes(root.right)]


def load_tree_solution(filename):
    """Load a solution and give it a TreeNode to construct nodes with."""
    module = load_solution(filename)
    module.TreeNode = TreeNode
    return module
