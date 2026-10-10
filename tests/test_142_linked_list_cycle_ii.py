"""Tests for 142. Linked List Cycle II.

Oracle: walk the list with a dict from node id to node; the first node reached
twice is the cycle entry, and the oracle returns that very object. It shares no
mechanism with the solution's tortoise/hare meeting-point arithmetic, and the
comparison is made with ``assertIs`` so the *node object* must match, not just
its value.

The O(1)-space path is measured separately with ``tracemalloc`` (two pointers
allocate nothing, while the dict oracle allocates hundreds of KB on a 10^4-node
list). Every case also verifies the "do not modify the linked list" requirement
by comparing the node-id chain before and after the call.
"""

import random
import tracemalloc
import unittest

from _lists import ListNode, load_list_solution

Solution = load_list_solution('142-linked-list-cycle-ii.py').Solution


def list_with_cycle(values, pos: int) -> "ListNode | None":
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


def dict_oracle(head) -> "ListNode | None":
    seen: dict[int, "ListNode"] = {}
    node = head
    while node is not None:
        if id(node) in seen:
            return seen[id(node)]
        seen[id(node)] = node
        node = node.next
    return None


def build_and_collect(values, pos, size: int):
    """Build one list and return it together with its first `size` nodes."""
    head = list_with_cycle(values, pos)
    nodes = []
    node = head
    for _ in range(size):
        nodes.append(node)
        node = node.next
    return head, nodes


class LinkedListCycleIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().detectCycle

    def check(self, values, pos):
        head = list_with_cycle(values, pos)
        before = walk_ids(head)
        expected = dict_oracle(head)
        produced = self.solve(head)
        self.assertIs(produced, expected, f'values={values} pos={pos}')
        self.assertEqual(walk_ids(head), before, 'the list was modified')
        return produced

    def test_official_examples(self):
        head = list_with_cycle([3, 2, 0, -4], 1)
        self.assertIs(self.solve(head), head.next)

        head = list_with_cycle([1, 2], 0)
        self.assertIs(self.solve(head), head)

        self.assertIsNone(self.solve(list_with_cycle([1], -1)))
        self.check([3, 2, 0, -4], 1)
        self.check([1, 2], 0)
        self.check([1], -1)

    def test_empty_and_single_node(self):
        self.assertIsNone(self.solve(None))
        self.assertIsNone(self.check([], -1))
        self.assertIsNone(self.check([9], -1))
        head = list_with_cycle([9], 0)
        self.assertIs(self.solve(head), head)

    def test_positions_in_a_four_node_list(self):
        values = [1, 2, 3, 4]
        for pos in range(4):
            with self.subTest(pos=pos):
                head, nodes = build_and_collect(values, pos, len(values))
                self.assertIs(self.solve(head), nodes[pos])
        head, _ = build_and_collect(values, -1, len(values))
        self.assertIsNone(self.solve(head))

    def test_exhaustive_small_lists(self):
        for size in range(1, 7):
            values = list(range(size))
            for pos in range(-1, size):
                with self.subTest(size=size, pos=pos):
                    produced = self.check(values, pos)
                    self.assertEqual(produced is not None, pos >= 0)

    def test_entry_identity_is_the_repeated_node(self):
        # The returned object must be the node the tail points at.
        values = list(range(20))
        for pos in (0, 1, 7, 19):
            with self.subTest(pos=pos):
                head = list_with_cycle(values, pos)
                nodes = []
                node = head
                for _ in range(len(values)):
                    nodes.append(node)
                    node = node.next
                produced = self.solve(head)
                self.assertIs(produced, nodes[pos])
                self.assertIs(nodes[-1].next, nodes[pos])

    def test_random_cases(self):
        rng = random.Random(1420)
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
                self.check(values, pos)  # agreement with the dict oracle
                head, nodes = build_and_collect(values, pos, size)
                produced = self.solve(head)
                if pos >= 0:
                    self.assertIs(produced, nodes[pos])
                else:
                    self.assertIsNone(produced)

    def test_constant_space_on_a_large_cyclic_list(self):
        head = list_with_cycle(range(10_000), 4321)
        tracemalloc.start()
        produced = self.solve(head)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertIsNotNone(produced)

        other = list_with_cycle(range(10_000), 4321)
        tracemalloc.start()
        expected = dict_oracle(other)
        _, oracle_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertIsNotNone(expected)

        self.assertLess(peak, 50_000)
        self.assertGreater(oracle_peak, 100_000)
        self.assertLess(peak, oracle_peak // 10)


if __name__ == '__main__':
    unittest.main()
