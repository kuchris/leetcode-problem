"""Biweekly Contest 193 Q3/Q4: literal oracles and constraint-sized cases."""

import itertools
import random
import unittest
from pathlib import Path

from _loader import load_solution


CONTEST_DIR = Path(__file__).resolve().parents[1] / 'contest' / 'Biweekly Contest 193'
Q3 = load_solution('q3-longest-resilient-subarray-ii.py', CONTEST_DIR).Solution
Q4 = load_solution('q4-minimize-inversions-in-a-prefix-tree.py', CONTEST_DIR).Solution


def brute_resilient(nums, k):
    best = 1
    for left in range(len(nums)):
        for right in range(left + 1, len(nums) + 1):
            values = nums[left:right]
            if all(sum(values[:i] + values[i + 1:]) % k == 0
                   for i in range(len(values))):
                best = max(best, len(values))
    return best


def brute_trie(words, target):
    """Build an explicit trie, enumerate actual traversals, count inversions."""
    root = {}
    for index, word in enumerate(words):
        node = root
        for char in word:
            node = node.setdefault(char, {})
        node['#'] = index

    def traversals(node):
        head = [node['#']] if '#' in node else []
        children = [traversals(child) for char, child in node.items() if char != '#']
        if not children:
            return [head]
        result = []
        for permutation in itertools.permutations(range(len(children))):
            for choice in itertools.product(*(children[i] for i in permutation)):
                result.append(head + [index for block in choice for index in block])
        return result

    position = {index: rank for rank, index in enumerate(target)}
    return min(
        sum(position[order[i]] > position[order[j]]
            for i in range(len(order)) for j in range(i + 1, len(order)))
        for order in traversals(root)
    )


class ResilientSubarrayIITests(unittest.TestCase):
    def test_examples(self):
        for nums, k, expected in (
            ([2, 4, 6, 3], 2, 3),
            ([1, 4, 7, 1], 3, 4),
            ([5, 5, 4, 8], 4, 2),
        ):
            self.assertEqual(Q3().resilientSubarray(nums, k), expected)

    def test_literal_oracle(self):
        rng = random.Random(19303)
        for _ in range(500):
            nums = [rng.randint(1, 20) for _ in range(rng.randint(1, 10))]
            k = rng.randint(1, 15)
            with self.subTest(nums=nums, k=k):
                self.assertEqual(Q3().resilientSubarray(nums, k), brute_resilient(nums, k))

    def test_constraint_size(self):
        self.assertEqual(Q3().resilientSubarray([100000] * 100000, 100000), 100000)
        self.assertEqual(Q3().resilientSubarray([1] * 100000, 100000), 1)
        self.assertEqual(Q3().resilientSubarray([1] * 100000, 99999), 100000)
        self.assertEqual(Q3().resilientSubarray([1] * 100000, 5), 99996)
        self.assertEqual(Q3().resilientSubarray([1, 2] * 50000, 2), 1)
        self.assertEqual(Q3().resilientSubarray([1, 2] * 50000, 1), 100000)

    def test_input_unchanged(self):
        nums = [2, 4, 6, 3]
        Q3().resilientSubarray(nums, 2)
        self.assertEqual(nums, [2, 4, 6, 3])


class PrefixTreeInversionTests(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(Q4().minInversions(['bad', 'bag', 'fig', 'fed'], [3, 1, 0, 2]), 2)
        self.assertEqual(Q4().minInversions(['ab', 'ac', 'ba', 'bc'], [0, 3, 1, 2]), 1)

    def test_prefix_words(self):
        words = ['a', 'ab', 'abc', 'ac', 'b']
        for target in itertools.permutations(range(len(words))):
            target = list(target)
            self.assertEqual(Q4().minInversions(words, target), brute_trie(words, target))

    def test_exhaustive_traversal_oracle(self):
        rng = random.Random(19304)
        pool = [''.join(chars) for size in range(1, 4)
                for chars in itertools.product('abc', repeat=size)]
        for _ in range(500):
            words = rng.sample(pool, rng.randint(1, 7))
            target = list(range(len(words)))
            rng.shuffle(target)
            with self.subTest(words=words, target=target):
                self.assertEqual(Q4().minInversions(words, target), brute_trie(words, target))

    def test_deep_chain_forced_order(self):
        words = ['a' * length for length in range(1, 21)]
        self.assertEqual(Q4().minInversions(words, list(range(20))), 0)
        self.assertEqual(Q4().minInversions(words, list(reversed(range(20)))), 190)

    def test_ten_children(self):
        self.assertEqual(Q4().minInversions(list('abcdefghij'), [9, 2, 7, 0, 4, 6, 1, 8, 5, 3]), 0)

    def test_constraint_size(self):
        # 10,000 unique length-20 words, with 1,111 full ten-child branch nodes.
        # Reverse lexicographic order is achievable by reversing children everywhere.
        words = [''.join(chars) + 'a' * 16
                 for chars in itertools.product('abcdefghij', repeat=4)]
        target = list(reversed(range(len(words))))
        self.assertEqual(Q4().minInversions(words, target), 0)

    def test_input_unchanged(self):
        words = ['a', 'ab', 'b']
        target = [1, 2, 0]
        Q4().minInversions(words, target)
        self.assertEqual(words, ['a', 'ab', 'b'])
        self.assertEqual(target, [1, 2, 0])


if __name__ == '__main__':
    unittest.main()
