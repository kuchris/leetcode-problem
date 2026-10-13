"""Tests for 160. Intersection of Two Linked Lists.

The requirement is node *identity*, not value equality, so:

  - the oracle collects the ids of list A's nodes and returns the first node of
    list B whose id is in that set;
  - every assertion about the result uses `is`, and one case deliberately puts
    nodes with equal values on both sides ahead of the real intersection, so a
    value-matching solution fails;
  - the lists' contents and node order are snapshotted before the call and
    compared afterwards, because the statement requires the structure to survive.

The pairs in the sweeps are built by constructing one shared suffix chain and
appending separate prefix chains to it, which is exactly the structure the
judge's skipA/skipB inputs describe.
"""

import itertools
import random
import unittest

from _lists import ListNode, build, load_list_solution, to_list

module = load_list_solution('160-intersection-of-two-linked-lists.py')
Solution = module.Solution


def chain_with_suffix(values, suffix):
    """Build a chain from `values` whose last node links to `suffix`."""
    head = None
    for value in reversed(list(values)):
        head = ListNode(value, head)
    if head is None:
        return suffix
    node = head
    while node.next is not None:
        node = node.next
    node.next = suffix
    return head


def make_pair(values_a, values_b, skip_a, skip_b):
    """Two lists sharing A's suffix from skip_a (and B's from skip_b).

    A skip equal to the list's length means "no intersection", matching the
    judge's convention that intersectVal is 0 and the skips are the lengths.
    """
    if skip_a >= len(values_a) or skip_b >= len(values_b):
        suffix = None
    else:
        suffix = build(values_a[skip_a:])
    head_a = chain_with_suffix(values_a[:skip_a], suffix)
    head_b = chain_with_suffix(values_b[:skip_b], suffix)
    return head_a, head_b, suffix


def identity_oracle(head_a, head_b):
    """The first node of B that is the very same object as a node of A."""
    seen = set()
    node = head_a
    while node is not None:
        seen.add(id(node))
        node = node.next
    node = head_b
    while node is not None:
        if id(node) in seen:
            return node
        node = node.next
    return None


def node_ids(head) -> list:
    ids = []
    node = head
    while node is not None:
        ids.append(id(node))
        node = node.next
    return ids


class IntersectionOfTwoLinkedListsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().getIntersectionNode

    def test_official_examples(self):
        cases = [([4, 1, 8, 4, 5], [5, 6, 1, 8, 4, 5], 2, 3, 8),
                 ([1, 9, 1, 2, 4], [3, 2, 4], 3, 1, 2),
                 ([2, 6, 4], [1, 5], 3, 2, None)]
        for values_a, values_b, skip_a, skip_b, expected_value in cases:
            with self.subTest(values_a=values_a, values_b=values_b):
                head_a, head_b, suffix = make_pair(values_a, values_b, skip_a, skip_b)
                result = self.solve(head_a, head_b)
                if expected_value is None:
                    self.assertIsNone(result)
                else:
                    self.assertIs(result, suffix)
                    self.assertEqual(result.val, expected_value)

    def test_returns_the_identical_object(self):
        head_a, head_b, suffix = make_pair([4, 1, 8, 4, 5],
                                           [5, 6, 1, 8, 4, 5], 2, 3)
        result = self.solve(head_a, head_b)
        self.assertIs(result, suffix)
        self.assertIs(result, identity_oracle(head_a, head_b))

    def test_equal_values_do_not_count_as_an_intersection(self):
        # Both prefixes contain 8s that are different objects; the shared suffix
        # also starts with an 8. A value-matching solution returns the wrong one.
        shared = build([8, 9])
        head_a = chain_with_suffix([8, 8], shared)
        head_b = chain_with_suffix([8], shared)
        result = self.solve(head_a, head_b)
        self.assertIs(result, shared)
        self.assertIsNot(result, head_a)
        self.assertIsNot(result, head_a.next)

    def test_two_separate_lists_with_equal_values_never_intersect(self):
        head_a = build([1, 2, 3])
        head_b = build([1, 2, 3])
        self.assertIsNone(self.solve(head_a, head_b))
        self.assertIsNone(identity_oracle(head_a, head_b))

    def test_intersection_at_every_offset(self):
        for skip_a in range(5):
            for skip_b in range(4):
                values_a = [1, 2, 3, 4, 5]
                values_b = [6, 7, 8, 9]
                with self.subTest(skip_a=skip_a, skip_b=skip_b):
                    head_a, head_b, suffix = make_pair(values_a, values_b, skip_a, skip_b)
                    result = self.solve(head_a, head_b)
                    if suffix is None:
                        self.assertIsNone(result)
                    else:
                        self.assertIs(result, suffix)
                    self.assertIs(result, identity_oracle(head_a, head_b))

    def test_intersection_at_the_very_first_node(self):
        shared = build([9, 9])
        head_a = shared
        head_b = chain_with_suffix([1, 2, 3], shared)
        self.assertIs(self.solve(head_a, head_b), shared)

    def test_single_node_lists(self):
        shared = ListNode(5)
        self.assertIs(self.solve(shared, shared), shared)
        self.assertIsNone(self.solve(ListNode(5), ListNode(5)))
        self.assertIsNone(self.solve(ListNode(1), ListNode(2)))

    def test_lists_are_not_modified(self):
        head_a, head_b, _ = make_pair([4, 1, 8, 4, 5], [5, 6, 1, 8, 4, 5], 2, 3)
        values_a, values_b = to_list(head_a), to_list(head_b)
        ids_a, ids_b = node_ids(head_a), node_ids(head_b)
        self.solve(head_a, head_b)
        self.assertEqual(to_list(head_a), values_a)
        self.assertEqual(to_list(head_b), values_b)
        self.assertEqual(node_ids(head_a), ids_a)
        self.assertEqual(node_ids(head_b), ids_b)

    def test_exhaustive_small_pairs(self):
        alphabet = (1, 2)
        for suffix_length in range(4):
            suffixes = [tuple(values) for values in
                        itertools.product(alphabet, repeat=suffix_length)]
            for prefix_a in itertools.product(alphabet, repeat=3):
                for prefix_b in itertools.product(alphabet, repeat=3):
                    for suffix_values in suffixes:
                        for shared in (True, False):
                            with self.subTest(prefix_a=prefix_a, prefix_b=prefix_b,
                                              suffix=suffix_values, shared=shared):
                                suffix = build(suffix_values) if shared else None
                                head_a = chain_with_suffix(prefix_a, suffix)
                                head_b = chain_with_suffix(prefix_b, suffix)
                                result = self.solve(head_a, head_b)
                                self.assertIs(result, identity_oracle(head_a, head_b))
                                if shared:
                                    self.assertIs(result, suffix)
                                else:
                                    self.assertIsNone(result)

    def test_randomised_pairs(self):
        rng = random.Random(1600)
        for _ in range(300):
            length_a = rng.randint(1, 25)
            length_b = rng.randint(1, 25)
            shared = rng.random() < 0.7 and length_a > 0 and length_b > 0
            suffix_length = rng.randint(1, 10) if shared else 0
            skip_a = rng.randint(0, length_a - 1) if shared else length_a
            skip_b = rng.randint(0, length_b - 1) if shared else length_b
            values_a = [rng.randint(1, 10 ** 5) for _ in range(length_a)]
            values_b = [rng.randint(1, 10 ** 5) for _ in range(length_b)]
            with self.subTest(length_a=length_a, length_b=length_b, shared=shared):
                if shared:
                    suffix = build([rng.randint(1, 10 ** 5) for _ in range(suffix_length)])
                    head_a = chain_with_suffix(values_a[:skip_a], suffix)
                    head_b = chain_with_suffix(values_b[:skip_b], suffix)
                    self.assertIs(self.solve(head_a, head_b), suffix)
                else:
                    head_a, head_b = build(values_a), build(values_b)
                    self.assertIsNone(self.solve(head_a, head_b))

    def test_constraint_sized(self):
        # m = n = 3 * 10^4 nodes is the constraint maximum.
        size = 3 * 10 ** 4
        suffix_length = 10 ** 4
        values = [index % 10 ** 5 + 1 for index in range(size)]
        suffix = build(values[:suffix_length])
        head_a = chain_with_suffix(values[:size - suffix_length], suffix)
        head_b = chain_with_suffix(values[:size - suffix_length], suffix)
        self.assertEqual(to_list(head_a)[-1], values[suffix_length - 1])

        result = self.solve(head_a, head_b)
        self.assertIs(result, suffix)
        self.assertIs(result, identity_oracle(head_a, head_b))

        # The same size with no intersection at all.
        head_a = build(values)
        head_b = build(values)
        self.assertIsNone(self.solve(head_a, head_b))

        # Intersection only at the final node, with the list still at the
        # constraint maximum of 3 * 10^4 nodes.
        last = ListNode(1)
        head_a = chain_with_suffix(values[:size - 1], last)
        head_b = chain_with_suffix(values[:size - 1], last)
        self.assertIs(self.solve(head_a, head_b), last)


if __name__ == '__main__':
    unittest.main()
