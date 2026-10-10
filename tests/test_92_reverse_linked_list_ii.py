"""Tests for 92. Reverse Linked List II.

Oracle: reverse the sub-list with Python slices,
values[:left-1] + values[left-1:right][::-1] + values[right:]. It never walks a
chain, so it checks the result independently of the in-place pointer surgery.

The identity check makes sure the nodes are re-linked rather than rebuilt.
"""

import itertools
import random
import unittest

from _lists import build, load_list_solution, to_list

Solution = load_list_solution('92-reverse-linked-list-ii.py').Solution


def brute_force(values: list[int], left: int, right: int) -> list[int]:
    return values[:left - 1] + values[left - 1:right][::-1] + values[right:]


class ReverseLinkedListIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().reverseBetween

    def reverse(self, values, left, right):
        return to_list(self.solve(build(values), left, right))

    def test_official_examples(self):
        self.assertEqual(self.reverse([1, 2, 3, 4, 5], 2, 4), [1, 4, 3, 2, 5])
        self.assertEqual(self.reverse([5], 1, 1), [5])

    def test_single_node(self):
        self.assertEqual(self.reverse([7], 1, 1), [7])
        self.assertEqual(self.reverse([-500], 1, 1), [-500])

    def test_left_equals_right_is_a_no_op(self):
        values = [1, 2, 3, 4, 5]
        for position in range(1, 6):
            with self.subTest(position=position):
                self.assertEqual(self.reverse(values, position, position), values)

    def test_two_nodes(self):
        self.assertEqual(self.reverse([1, 2], 1, 2), [2, 1])
        self.assertEqual(self.reverse([1, 2], 1, 1), [1, 2])
        self.assertEqual(self.reverse([1, 2], 2, 2), [1, 2])

    def test_whole_list_reversed(self):
        values = [1, 2, 3, 4, 5, 6]
        self.assertEqual(self.reverse(values, 1, 6), values[::-1])

    def test_prefix_and_suffix_segments(self):
        values = [1, 2, 3, 4, 5]
        self.assertEqual(self.reverse(values, 1, 2), [2, 1, 3, 4, 5])
        self.assertEqual(self.reverse(values, 4, 5), [1, 2, 3, 5, 4])
        self.assertEqual(self.reverse(values, 1, 1), values)
        self.assertEqual(self.reverse(values, 5, 5), values)

    def test_boundary_values(self):
        values = [-500, -500, 0, 500, 500]
        for left, right in ((1, 5), (2, 4), (1, 2), (4, 5)):
            with self.subTest(left=left, right=right):
                self.assertEqual(
                    self.reverse(values, left, right), brute_force(values, left, right)
                )

    def test_duplicate_values(self):
        values = [1, 1, 1, 1]
        for left, right in ((1, 4), (2, 3), (1, 2)):
            with self.subTest(left=left, right=right):
                self.assertEqual(self.reverse(values, left, right), values)

    def test_nodes_are_reused_not_rebuilt(self):
        values = [1, 2, 3, 4, 5]
        head = build(values)
        original = []
        node = head
        while node is not None:
            original.append(node)
            node = node.next

        result = self.solve(head, 2, 4)
        walked = []
        node = result
        while node is not None and len(walked) <= len(original):
            walked.append(node)
            node = node.next
        self.assertIsNone(node, 'the result chain must not contain a cycle')
        self.assertEqual(len(walked), len(original))
        for node in walked:
            self.assertIn(node, original)

    def test_exhaustive_small_cases(self):
        for size in range(1, 7):
            for values in itertools.product(range(3), repeat=size):
                values = list(values)
                for left in range(1, size + 1):
                    for right in range(left, size + 1):
                        with self.subTest(values=values, left=left, right=right):
                            self.assertEqual(
                                self.reverse(values, left, right),
                                brute_force(values, left, right),
                            )

    def test_randomised_cases(self):
        rng = random.Random(920)
        for _ in range(200):
            size = rng.randint(1, 40)
            values = [rng.randint(-500, 500) for _ in range(size)]
            left = rng.randint(1, size)
            right = rng.randint(left, size)
            with self.subTest(size=size, left=left, right=right):
                self.assertEqual(
                    self.reverse(values, left, right), brute_force(values, left, right)
                )

    def test_constraint_sized(self):
        # 500 nodes is the constraint maximum.
        rng = random.Random(921)
        values = [rng.randint(-500, 500) for _ in range(500)]
        for left, right in ((1, 500), (1, 2), (499, 500), (250, 251), (250, 260),
                            (2, 499), (100, 400)):
            with self.subTest(left=left, right=right):
                self.assertEqual(
                    self.reverse(values, left, right), brute_force(values, left, right)
                )

        # A long list of one repeated value must survive a full reversal.
        values = [500] * 500
        self.assertEqual(self.reverse(values, 1, 500), values)


if __name__ == '__main__':
    unittest.main()
