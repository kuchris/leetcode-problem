"""Undirected graph nodes for problem 133 (Clone Graph).

The judge injects a ``Node`` with ``val`` and ``neighbors``; these helpers build
a graph from LeetCode's adjacency-list test format and read one back. Reading a
graph back only follows ``neighbors`` pointers, so it is usable as an oracle for
a cloning solution and also detects the two things serialization alone cannot:
whether the copy reuses original node objects, and whether a value maps to more
than one object.
"""

from _loader import load_solution


class Node:
    """Stand-in for the Node that LeetCode injects via its preamble."""

    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def build(adjacency) -> "Node | None":
    """Build a graph from an adjacency list; values are 1-indexed there."""
    if not adjacency:
        return None
    nodes = {index + 1: Node(index + 1) for index in range(len(adjacency))}
    for index, neighbors in enumerate(adjacency):
        nodes[index + 1].neighbors = [nodes[value] for value in neighbors]
    return nodes[1]


def graph_nodes(node) -> dict:
    """{val: Node} for every node reachable from ``node``, iteratively."""
    found: dict = {}
    stack = [node] if node is not None else []
    while stack:
        current = stack.pop()
        if current.val in found:
            continue
        found[current.val] = current
        stack.extend(current.neighbors)
    return found


def to_adjacency(node) -> list:
    """Serialize to the adjacency-list format, indexed by value."""
    found = graph_nodes(node)
    if not found:
        return []
    size = len(found)
    return [[neighbor.val for neighbor in found[value].neighbors]
            for value in range(1, size + 1)]


def canonical(adjacency) -> list:
    """Adjacency list with each neighbour list sorted (order is not significant)."""
    return [sorted(neighbors) for neighbors in adjacency]


def load_graph_solution(filename):
    """Load a solution and give it this Node class to construct nodes with."""
    module = load_solution(filename)
    module.Node = Node
    return module
