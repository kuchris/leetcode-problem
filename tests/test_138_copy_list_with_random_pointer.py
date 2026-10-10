"""Tests for 138. Copy List with Random Pointer.

Serialization alone cannot prove a real deep copy, so the checks are layered:

  - `serialize(copy)` must equal `serialize(origin)`; it raises when a random
    pointer aims outside the chain it is reading, so a random pointer left
    pointing at an original node is detected rather than silently resolved;
  - the two sets of node objects must be disjoint by identity;
  - the copy must hold exactly one new object per position, and its head must not
    be the original head.

Inputs are generated in the problem's own ``[[val, random_index], ...]`` format,
where every random index is in range or null, matching the guarantee.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _random_list_nodes import build, load_random_list_solution, nodes, serialize

module = load_random_list_solution('138-copy-list-with-random-pointer.py')
Solution = module.Solution


def random_pairs(rng, size: int) -> list:
    """A random list in the official format."""
    return [[rng.randint(-10 ** 4, 10 ** 4),
             None if rng.random() < 0.3 else rng.randrange(size)]
            for _ in range(size)]


class CopyListWithRandomPointerTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().copyRandomList

    def assert_deep_copy(self, origin, copy):
        origin_nodes = nodes(origin)
        copy_nodes = nodes(copy)

        self.assertIsNot(copy, origin)
        self.assertEqual(len(copy_nodes), len(origin_nodes))
        self.assertEqual([node.val for node in copy_nodes], [node.val for node in origin_nodes])
        # Raises if any next/random pointer of the copy leaves the copied chain.
        self.assertEqual(serialize(copy), serialize(origin))
        self.assertEqual({id(node) for node in copy_nodes}
                         & {id(node) for node in origin_nodes}, set())
        self.assertEqual(len({id(node) for node in copy_nodes}), len(copy_nodes))

    def test_official_examples(self):
        for pairs in ([[7, None], [13, 0], [11, 4], [10, 2], [1, 0]],
                      [[1, 1], [2, 1]],
                      [[3, None], [3, 0], [3, None]]):
            with self.subTest(pairs=pairs):
                origin = build(pairs)
                self.assert_deep_copy(origin, self.solve(origin))

    def test_empty_list(self):
        self.assertIsNone(self.solve(None))
        self.assertIsNone(self.solve(build([])))

    def test_single_node(self):
        self.assert_deep_copy(build([[5, None]]), self.solve(build([[5, None]])))

    def test_single_node_pointing_at_itself(self):
        origin = build([[5, 0]])
        copy = self.solve(origin)
        self.assert_deep_copy(origin, copy)
        self.assertIs(copy.random, copy)
        self.assertIsNot(copy.random, origin)

    def test_random_pointers_are_relative_not_value_based(self):
        # Three equal values: the pointers must follow positions, not values.
        pairs = [[3, 2], [3, 2], [3, 0]]
        origin = build(pairs)
        copy = self.solve(origin)
        self.assert_deep_copy(origin, copy)
        self.assertIs(copy.random, copy.next.next)
        self.assertIs(copy.next.random, copy.next.next)

    def test_original_is_not_modified(self):
        pairs = [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]
        origin = build(pairs)
        before = serialize(origin)
        before_ids = [id(node) for node in nodes(origin)]
        self.solve(origin)
        self.assertEqual(serialize(origin), before)
        self.assertEqual([id(node) for node in nodes(origin)], before_ids)

    def test_every_random_pointer_target_is_copied(self):
        pairs = [[1, 4], [2, 2], [3, 0], [4, None], [5, 3]]
        origin = build(pairs)
        copy = self.solve(origin)
        self.assert_deep_copy(origin, copy)
        origin_nodes = nodes(origin)
        copy_nodes = nodes(copy)
        for index, node in enumerate(origin_nodes):
            if node.random is None:
                self.assertIsNone(copy_nodes[index].random)
            else:
                self.assertIs(copy_nodes[index].random,
                              copy_nodes[origin_nodes.index(node.random)])

    def test_exhaustive_small_lists(self):
        for size in range(1, 4):
            choices = [None] + list(range(size))
            for pairs in itertools.product(choices, repeat=size):
                for values in itertools.product((1, -2), repeat=size):
                    pairs_ = [[value, random_index]
                              for value, random_index in zip(values, pairs)]
                    with self.subTest(pairs=pairs_):
                        origin = build(pairs_)
                        self.assert_deep_copy(origin, self.solve(origin))

    def test_exhaustive_four_nodes_equal_values(self):
        size = 4
        choices = [None] + list(range(size))
        for random_indices in itertools.product(choices, repeat=size):
            pairs = [[1, random_index] for random_index in random_indices]
            with self.subTest(pairs=pairs):
                origin = build(pairs)
                self.assert_deep_copy(origin, self.solve(origin))

    def test_randomised_cases(self):
        rng = random.Random(1380)
        for _ in range(300):
            size = rng.randint(1, 60)
            pairs = random_pairs(rng, size)
            with self.subTest(size=size):
                origin = build(pairs)
                self.assert_deep_copy(origin, self.solve(origin))

    def test_constraint_sized(self):
        size = 1000  # the constraint maximum
        rng = random.Random(1381)

        patterns = {
            'no randoms': [[index, None] for index in range(size)],
            'self pointers': [[index, index] for index in range(size)],
            'next node': [[index, (index + 1) % size] for index in range(size)],
            'mirrored': [[index, size - 1 - index] for index in range(size)],
            'last node': [[index, size - 1] for index in range(size)],
            'random': random_pairs(rng, size),
        }
        for name, pairs in patterns.items():
            with self.subTest(pattern=name):
                origin = build(pairs)
                self.assertEqual(len(nodes(origin)), size)
                self.assert_deep_copy(origin, self.solve(origin))


if __name__ == '__main__':
    unittest.main()
