"""Tests for 141. Linked List Cycle.

Oracle: walk the list keeping a set of the ids of the nodes already seen; the
first node seen twice proves a cycle. It shares no mechanism with the solution's
two-pointer walk (no tortoise, no hare, no arithmetic), so it is an independent
authority, and it is cycle-safe because it stops at the first repeat.

The O(1)-space path is tested separately: ``tracemalloc`` measures the peak
Python allocation of the solution on a 10^4-node cyclic list (two local pointers,
so ~0 bytes) and compares it with the same measurement for the set oracle
(hundreds of KB), which both proves the solution allocates nothing per node and
shows the measurement itself is meaningful. Every case also checks that the list
is left untouched.
"""

import random
import tracemalloc
import unittest

from _lists import ListNode, load_list_solution

Solution = load_list_solution('141-linked-list-cycle.py').Solution


def list_with_cycle(values, pos: int) -> "ListNode | None":
    """Build a list from values; if pos >= 0, tail.next points at index pos."""
    head = None
    for value in reversed(list(values)):
        head = ListNode(value, head)
    if pos >= 0:
        nodes = []
        node = head
        while node is not None:
            nodes.append(node)
            node = node.next
        nodes[-1].next = nodes[pos]
    return head


def walk_ids(head) -> list:
    """Node ids along the chain, stopping at the first repeat."""
    seen = set()
    ids = []
    node = head
    while node is not None:
        if id(node) in seen:
            ids.append(id(node))
            break
        seen.add(id(node))
        ids.append(id(node))
        node = node.next
    return ids


def set_oracle(head) -> bool:
    seen = set()
    node = head
    while node is not None:
        if id(node) in seen:
            return True
        seen.add(id(node))
        node = node.next
    return False


class LinkedListCycleTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().hasCycle

    def check(self, values, pos):
        head = list_with_cycle(values, pos)
        before = walk_ids(head)
        produced = self.solve(head)
        self.assertEqual(produced, set_oracle(head), f'values={values} pos={pos}')
        self.assertEqual(walk_ids(head), before, 'the list was modified')
        return produced

    def test_official_examples(self):
        self.assertTrue(self.solve(list_with_cycle([3, 2, 0, -4], 1)))
        self.assertTrue(self.solve(list_with_cycle([1, 2], 0)))
        self.assertFalse(self.solve(list_with_cycle([1], -1)))
        self.check([3, 2, 0, -4], 1)
        self.check([1, 2], 0)
        self.check([1], -1)

    def test_empty_and_single_node(self):
        self.assertFalse(self.solve(None))
        self.assertFalse(self.check([], -1))
        self.assertFalse(self.check([7], -1))
        self.assertTrue(self.check([7], 0))

    def test_two_and_three_nodes(self):
        self.assertTrue(self.check([1, 2], 1))
        self.assertTrue(self.check([1, 2], 0))
        self.assertFalse(self.check([1, 2], -1))
        self.assertTrue(self.check([1, 2, 3], 0))
        self.assertTrue(self.check([1, 2, 3], 1))
        self.assertTrue(self.check([1, 2, 3], 2))
        self.assertFalse(self.check([1, 2, 3], -1))

    def test_exhaustive_small_lists(self):
        for size in range(1, 7):
            values = list(range(size))
            for pos in range(-1, size):
                with self.subTest(size=size, pos=pos):
                    expected = pos >= 0
                    self.assertEqual(self.check(values, pos), expected)

    def test_cycle_that_revisits_the_head_only_via_the_loop(self):
        # A long tail and a cycle that closes on the head.
        values = list(range(50))
        self.assertTrue(self.check(values, 0))
        self.assertTrue(self.check(values, 49))

    def test_random_cases(self):
        rng = random.Random(1410)
        for _ in range(200):
            size = rng.randint(0, 200)
            values = [rng.randint(-100_000, 100_000) for _ in range(size)]
            pos = -1 if rng.random() < 0.5 or size == 0 else rng.randrange(size)
            with self.subTest(size=size, pos=pos):
                self.check(values, pos)

    def test_constraint_sized(self):
        # 10^4 nodes is the constraint maximum.
        size = 10_000
        values = list(range(size))
        for pos in (-1, 0, 1, 2, 5000, 9998, 9999):
            with self.subTest(pos=pos):
                self.check(values, pos)

        # A long tail with a long cycle.
        self.assertTrue(self.check(values, size // 2))
        # A long tail with a one-node cycle at the end.
        self.assertTrue(self.check(values, size - 1))

    def test_constant_space_on_a_large_cyclic_list(self):
        head = list_with_cycle(range(10_000), 4321)
        tracemalloc.start()
        self.assertTrue(self.solve(head))
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        other = list_with_cycle(range(10_000), 4321)
        tracemalloc.start()
        self.assertTrue(set_oracle(other))
        _, oracle_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Two pointers: essentially nothing is allocated.
        self.assertLess(peak, 50_000)
        # The set oracle really does allocate, which validates the measurement.
        self.assertGreater(oracle_peak, 100_000)
        self.assertLess(peak, oracle_peak // 10)


if __name__ == '__main__':
    unittest.main()
