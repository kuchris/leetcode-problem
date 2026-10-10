"""Binary trees whose nodes also carry a ``next`` pointer (problems 116 / 117).

The judge injects a ``Node`` class with ``val``, ``left``, ``right`` **and**
``next`` for those problems, so the plain :mod:`_trees` helpers cannot be used
as-is: they build ``TreeNode`` objects without the extra attribute.
"""

import collections

from _loader import load_solution


class Node:
    """Stand-in for the Node that LeetCode injects via its preamble."""

    def __init__(self, val=0, left=None, right=None, next=None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next


def build(values) -> "Node | None":
    """Build a tree from LeetCode's level-order list.

    Same layout as :func:`_trees.build`: ``None`` marks a missing child and the
    children of a missing node are not listed at all.
    """
    if not values:
        return None
    root = Node(values[0])
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
                child = Node(value)
                setattr(node, side, child)
                queue.append(child)
    return root


def levels(root) -> list:
    """Nodes grouped by depth, left to right.

    The grouping is computed with an ordinary queue and never reads ``next``,
    so it stays a valid oracle for solutions that are rewriting those pointers.
    """
    if root is None:
        return []
    groups = []
    queue = collections.deque([root])
    while queue:
        groups.append(list(queue))
        for _ in range(len(queue)):
            node = queue.popleft()
            for child in (node.left, node.right):
                if child is not None:
                    queue.append(child)
    return groups


def link_levels(root) -> "Node | None":
    """Definitional oracle: chain each level with a plain level-order BFS."""
    for group in levels(root):
        for left, right in zip(group, group[1:]):
            left.next = right
    return root


def serialize(root) -> list:
    """The problem's output format: each level's values then ``'#'``.

    A level is read by following ``next`` from its leftmost node, so a missing
    or misplaced link shows up in the result. The descent to the next level is
    done through the children, which keeps the reader honest.
    """
    values = []
    level_start = root
    while level_start is not None:
        next_start = None
        node = level_start
        while node is not None:
            for child in (node.left, node.right):
                if child is not None and next_start is None:
                    next_start = child
            node = node.next
        node = level_start
        while node is not None:
            values.append(node.val)
            node = node.next
        values.append('#')
        level_start = next_start
    return values


def to_structure(root):
    """Nested ``(val, next value, left, right)`` view; None for missing nodes."""
    if root is None:
        return None
    return (
        root.val,
        None if root.next is None else root.next.val,
        to_structure(root.left),
        to_structure(root.right),
    )


def load_next_tree_solution(filename):
    """Load a solution and give it this Node class to construct nodes with."""
    module = load_solution(filename)
    module.Node = Node
    return module
