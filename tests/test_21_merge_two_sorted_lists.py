import itertools
import unittest

from _loader import load_solution

module = load_solution('21-merge-two-sorted-lists.py')


class ListNode:
    """Stand-in for the ListNode that LeetCode injects via its preamble."""

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


# The solution resolves ListNode from its module globals at call time.
module.ListNode = ListNode
Solution = module.Solution


def build(values):
    head = None
    for value in reversed(values):
        head = ListNode(value, head)
    return head


def to_list(head) -> list[int]:
    values = []
    while head is not None:
        values.append(head.val)
        head = head.next
    return values


def brute_force(first: list[int], second: list[int]) -> list[int]:
    return sorted(first + second)


class MergeTwoSortedListsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().mergeTwoLists

    def merge(self, first, second):
        return to_list(self.solve(build(first), build(second)))

    def test_official_examples(self):
        self.assertEqual(self.merge([1, 2, 4], [1, 3, 4]), [1, 1, 2, 3, 4, 4])
        self.assertEqual(self.merge([], []), [])
        self.assertEqual(self.merge([], [0]), [0])

    def test_one_list_exhausted_first(self):
        self.assertEqual(self.merge([1, 2, 3], []), [1, 2, 3])
        self.assertEqual(self.merge([], [1, 2, 3]), [1, 2, 3])

    def test_negative_values_and_duplicates(self):
        self.assertEqual(self.merge([-100, -100, 0], [-100, 50, 100]),
                         [-100, -100, -100, 0, 50, 100])

    def test_maximum_size(self):
        first = list(range(0, 100, 2))
        second = list(range(1, 100, 2))
        self.assertEqual(self.merge(first, second), list(range(100)))

    def test_exhaustive_small_cases(self):
        pool = [-1, 0, 1, 2]
        for size_a in range(4):
            for size_b in range(4):
                for first in itertools.combinations_with_replacement(pool, size_a):
                    for second in itertools.combinations_with_replacement(pool, size_b):
                        with self.subTest(first=first, second=second):
                            self.assertEqual(
                                self.merge(list(first), list(second)),
                                brute_force(list(first), list(second)),
                            )


if __name__ == '__main__':
    unittest.main()
