"""Tests for 133. Clone Graph.

Serialization alone cannot distinguish a real deep copy from one that reuses the
original's node objects, so the checks are layered:

  - `to_adjacency` must reproduce the original adjacency list (each neighbour
    list is sorted first, since the format treats it as unordered);
  - the two sets of node objects must be disjoint by identity, which is what
    proves no object at any depth is shared;
  - the copy must hold exactly one distinct object per value, and reading it back
    only ever follows the copy's own neighbour pointers.

The graphs used in the sweep are generated from edge subsets and filtered to be
connected and simple, matching the guarantees (no self-loops, no repeated edges,
connected, values 1..n).
"""

import random
import unittest

from _graph_nodes import build, canonical, graph_nodes, load_graph_solution, to_adjacency

module = load_graph_solution('133-clone-graph.py')
Solution = module.Solution


def is_connected(adjacency) -> bool:
    """Breadth-first reachability over a plain adjacency list."""
    size = len(adjacency)
    if size == 0:
        return True
    seen = {1}
    queue = [1]
    while queue:
        node = queue.pop()
        for neighbor in adjacency[node - 1]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return len(seen) == size


def all_connected_graphs(size: int):
    """Every connected simple graph on values 1..size, as an adjacency list."""
    edges = [(i, j) for i in range(1, size + 1) for j in range(i + 1, size + 1)]
    for mask in range(1 << len(edges)):
        adjacency = [[] for _ in range(size)]
        for bit, (i, j) in enumerate(edges):
            if mask >> bit & 1:
                adjacency[i - 1].append(j)
                adjacency[j - 1].append(i)
        if is_connected(adjacency):
            yield adjacency


def random_connected_graph(rng, size: int) -> list:
    """A random connected simple graph: random tree plus extra random edges."""
    adjacency = [[] for _ in range(size)]
    order = list(range(1, size + 1))
    rng.shuffle(order)
    for index in range(1, size):
        parent = order[rng.randrange(index)]
        child = order[index]
        adjacency[parent - 1].append(child)
        adjacency[child - 1].append(parent)
    for i in range(1, size + 1):
        for j in range(i + 1, size + 1):
            if j not in adjacency[i - 1] and rng.random() < 0.15:
                adjacency[i - 1].append(j)
                adjacency[j - 1].append(i)
    return adjacency


class CloneGraphTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().cloneGraph

    def assert_deep_copy(self, original, copy):
        """The copy must match in shape and share no node object with the input."""
        original_nodes = graph_nodes(original)
        copy_nodes = graph_nodes(copy)

        self.assertIsNot(copy, original)
        self.assertEqual(sorted(copy_nodes), sorted(original_nodes))
        self.assertEqual(canonical(to_adjacency(copy)), canonical(to_adjacency(original)))

        # One distinct new object per value, and none of them from the original.
        self.assertEqual(len({id(node) for node in copy_nodes.values()}), len(copy_nodes))
        self.assertEqual(
            {id(node) for node in copy_nodes.values()}
            & {id(node) for node in original_nodes.values()},
            set(),
        )

    def test_official_examples(self):
        adjacency = [[2, 4], [1, 3], [2, 4], [1, 3]]
        original = build(adjacency)
        self.assert_deep_copy(original, self.solve(original))

        original = build([[]])
        self.assert_deep_copy(original, self.solve(original))

        self.assertIsNone(self.solve(build([])))

    def test_empty_graph(self):
        self.assertIsNone(self.solve(None))
        self.assertIsNone(self.solve(build([])))

    def test_single_node(self):
        original = build([[]])
        copy = self.solve(original)
        self.assertEqual(copy.val, 1)
        self.assertEqual(copy.neighbors, [])
        self.assertIsNot(copy, original)

    def test_single_node_with_every_value(self):
        for value in (1, 50, 100):
            with self.subTest(value=value):
                node = module.Node(value)
                copy = self.solve(node)
                self.assertEqual(copy.val, value)
                self.assertEqual(copy.neighbors, [])
                self.assertIsNot(copy, node)

    def test_two_nodes(self):
        original = build([[2], [1]])
        self.assert_deep_copy(original, self.solve(original))

    def test_cycle_must_not_reuse_the_original_nodes(self):
        adjacency = [[2], [3], [1]]
        original = build(adjacency)
        copy = self.solve(original)
        self.assert_deep_copy(original, copy)
        # Walk the copy's own cycle and confirm every step lands on a new node.
        first = copy
        second = copy.neighbors[0]
        third = second.neighbors[0]
        self.assertIs(third.neighbors[0], first)
        self.assertNotIn(id(first), {id(node) for node in graph_nodes(original).values()})

    def test_special_shapes(self):
        shapes = {
            'path': [[2], [1, 3], [2, 4], [3]],
            'star': [[2, 3, 4], [1], [1], [1]],
            'complete4': [[2, 3, 4], [1, 3, 4], [1, 2, 4], [1, 2, 3]],
            'triangle_with_tail': [[2, 3], [1, 3], [1, 2, 4], [3]],
        }
        for name, adjacency in shapes.items():
            with self.subTest(shape=name):
                original = build(adjacency)
                snapshot = canonical(to_adjacency(original))
                self.assert_deep_copy(original, self.solve(original))
                self.assertEqual(canonical(to_adjacency(original)), snapshot)

    def test_original_graph_is_not_modified(self):
        adjacency = [[2, 4], [1, 3], [2, 4], [1, 3]]
        original = build(adjacency)
        before_values = canonical(to_adjacency(original))
        before_ids = {value: id(node) for value, node in graph_nodes(original).items()}
        self.solve(original)
        self.assertEqual(canonical(to_adjacency(original)), before_values)
        self.assertEqual({value: id(node) for value, node in graph_nodes(original).items()},
                         before_ids)

    def test_exhaustive_connected_graphs(self):
        for size in range(1, 6):
            for adjacency in all_connected_graphs(size):
                with self.subTest(size=size, adjacency=canonical(adjacency)):
                    original = build(adjacency)
                    self.assert_deep_copy(original, self.solve(original))

    def test_randomised_graphs(self):
        rng = random.Random(1330)
        for _ in range(200):
            size = rng.randint(1, 40)
            adjacency = random_connected_graph(rng, size)
            with self.subTest(size=size):
                original = build(adjacency)
                self.assert_deep_copy(original, self.solve(original))

    def test_constraint_sized(self):
        rng = random.Random(1331)
        size = 100  # the constraint maximum

        path = [[2]] + [[value - 1, value + 1] for value in range(2, size)] + [[size - 1]]
        cycle = [[size if value == 1 else value - 1, 1 if value == size else value + 1]
                 for value in range(1, size + 1)]
        star = [[value for value in range(2, size + 1)]] + [[1] for _ in range(size - 1)]
        complete = [[other for other in range(1, size + 1) if other != value]
                    for value in range(1, size + 1)]

        for name, adjacency in (('path', path), ('cycle', cycle),
                                ('star', star), ('complete', complete),
                                ('random', random_connected_graph(rng, size))):
            with self.subTest(shape=name):
                original = build(adjacency)
                self.assertEqual(len(graph_nodes(original)), size)
                self.assert_deep_copy(original, self.solve(original))


if __name__ == '__main__':
    unittest.main()
