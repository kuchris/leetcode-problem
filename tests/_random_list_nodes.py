"""Linked-list nodes with an extra ``random`` pointer for problem 138.

The judge injects a ``Node`` with ``val``, ``next`` and ``random``, and the test
format is a list of ``[val, random_index]`` pairs. :func:`serialize` refuses to
report a random index that is not reachable through ``next`` from the head,
which is what makes it able to catch a copy whose random pointer still aims at a
node of the original list.
"""

from _loader import load_solution


class Node:
    """Stand-in for the Node that LeetCode injects via its preamble."""

    def __init__(self, x=0, next=None, random=None):
        self.val = int(x)
        self.next = next
        self.random = random


def build(pairs) -> "Node | None":
    """Build the list from ``[[val, random_index], ...]``."""
    if not pairs:
        return None
    created = [Node(pair[0]) for pair in pairs]
    for index in range(len(created) - 1):
        created[index].next = created[index + 1]
    for node, pair in zip(created, pairs):
        if pair[1] is not None:
            node.random = created[pair[1]]
    return created[0]


def nodes(head) -> list:
    """Every node object, in list order."""
    found = []
    node = head
    while node is not None:
        found.append(node)
        node = node.next
    return found


def serialize(head) -> list:
    """``[[val, random_index], ...]``; fails loudly on an outside random pointer."""
    found = nodes(head)
    positions = {id(node): index for index, node in enumerate(found)}
    result = []
    for node in found:
        if node.random is None:
            result.append([node.val, None])
        else:
            if id(node.random) not in positions:
                raise ValueError('a random pointer aims outside the copied list')
            result.append([node.val, positions[id(node.random)]])
    return result


def load_random_list_solution(filename):
    """Load a solution and give it this Node class to construct nodes with."""
    module = load_solution(filename)
    module.Node = Node
    return module
