"""Tests for 165. Compare Version Numbers.

The oracle converts every revision with `int()` and pads the shorter version with
zeros, which is a different algorithm from the solution's string comparison
(length first, then lexicographic). Because the two are supposed to agree for the
same reason, the sweep also checks two structural properties that hold for any
comparison: antisymmetry (compare(b, a) == -compare(a, b)) and transitivity on
sampled triples.

The long-revision cases are deliberately outside the stated 32-bit guarantee and
are labelled as such: they exist to show the comparison does not depend on
fixed-width parsing.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('165-compare-version-numbers.py').Solution


def int_oracle(version1: str, version2: str) -> int:
    """Compare revision by revision using integer values."""
    left = [int(part) for part in version1.split('.')]
    right = [int(part) for part in version2.split('.')]
    for index in range(max(len(left), len(right))):
        first = left[index] if index < len(left) else 0
        second = right[index] if index < len(right) else 0
        if first != second:
            return -1 if first < second else 1
    return 0


def version_strings(segment_pool, max_parts: int):
    """Every version built from 1..max_parts segments of the pool."""
    for parts in range(1, max_parts + 1):
        for segments in itertools.product(segment_pool, repeat=parts):
            yield '.'.join(segments)


class CompareVersionNumbersTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().compareVersion

    def test_official_examples(self):
        self.assertEqual(self.solve('1.2', '1.10'), -1)
        self.assertEqual(self.solve('1.01', '1.001'), 0)
        self.assertEqual(self.solve('1.0', '1.0.0.0'), 0)

    def test_trailing_zero_revisions_are_ignored(self):
        self.assertEqual(self.solve('1.0', '1'), 0)
        self.assertEqual(self.solve('1', '1.0'), 0)
        self.assertEqual(self.solve('1.0.0.0', '1'), 0)
        self.assertEqual(self.solve('1.0', '1.0.0.1'), -1)
        self.assertEqual(self.solve('1.0.1', '1.0'), 1)
        self.assertEqual(self.solve('0.0', '0'), 0)

    def test_leading_zeros_are_ignored(self):
        self.assertEqual(self.solve('1.01', '1.001'), 0)
        self.assertEqual(self.solve('01.0', '1'), 0)
        self.assertEqual(self.solve('1.010', '1.10'), 0)
        self.assertEqual(self.solve('0001.0002', '1.2'), 0)

    def test_revision_order_is_numeric_not_lexicographic(self):
        self.assertEqual(self.solve('1.2', '1.10'), -1)
        self.assertEqual(self.solve('1.10', '1.2'), 1)
        self.assertEqual(self.solve('2', '10'), -1)
        self.assertEqual(self.solve('1.9', '1.10'), -1)

    def test_missing_revisions_are_zero(self):
        self.assertEqual(self.solve('1', '1.1'), -1)
        self.assertEqual(self.solve('1.1', '1'), 1)
        self.assertEqual(self.solve('1.0.0', '1.0'), 0)
        self.assertEqual(self.solve('1.1.0.0.0', '1.1'), 0)

    def test_single_and_empty_style_versions(self):
        self.assertEqual(self.solve('0', '0'), 0)
        self.assertEqual(self.solve('0', '1'), -1)
        self.assertEqual(self.solve('1', '0'), 1)
        self.assertEqual(self.solve('1.0.0.0.0.0', '0'), 1)

    def test_exhaustive_small_cases(self):
        pool = ('0', '1', '2', '10')
        versions = list(version_strings(pool, 3))
        self.assertEqual(len(versions), 84)
        for first in versions:
            for second in versions:
                with self.subTest(first=first, second=second):
                    expected = int_oracle(first, second)
                    self.assertEqual(self.solve(first, second), expected)
                    self.assertEqual(self.solve(second, first), -expected)

    def test_transitivity_on_sampled_triples(self):
        rng = random.Random(1650)
        versions = list(version_strings(('0', '1', '2', '3', '10'), 3))
        for _ in range(300):
            first, second, third = (rng.choice(versions) for _ in range(3))
            with self.subTest(triple=(first, second, third)):
                ab = int_oracle(first, second)
                bc = int_oracle(second, third)
                self.assertEqual(self.solve(first, second), ab)
                self.assertEqual(self.solve(second, third), bc)
                if ab <= 0 and bc <= 0:
                    self.assertEqual(self.solve(first, third), int_oracle(first, third))
                    self.assertLessEqual(self.solve(first, third), 0)
                if ab >= 0 and bc >= 0:
                    self.assertGreaterEqual(self.solve(first, third), 0)

    def test_randomised_cases(self):
        rng = random.Random(1651)
        for _ in range(1500):
            parts = rng.randint(1, 8)
            first = '.'.join(str(rng.randint(0, 2 ** 31 - 1)) for _ in range(parts))
            second_parts = rng.randint(1, 8)
            second = '.'.join(str(rng.randint(0, 2 ** 31 - 1)) for _ in range(second_parts))
            with self.subTest(first=first, second=second):
                expected = int_oracle(first, second)
                self.assertEqual(self.solve(first, second), expected)
                self.assertEqual(self.solve(second, first), -expected)

    def test_randomised_with_leading_zeros(self):
        rng = random.Random(1652)
        for _ in range(500):
            parts = rng.randint(1, 6)
            segments = []
            for _ in range(parts):
                digits = str(rng.randint(0, 99))
                segments.append('0' * rng.randint(0, 4) + digits)
            first = '.'.join(segments)
            padded = [segment.lstrip('0') or '0' for segment in segments]
            if rng.random() < 0.5:
                second = '.'.join(padded + ['0'] * rng.randint(1, 3))
            else:
                second = '.'.join(padded)
            with self.subTest(first=first, second=second):
                self.assertEqual(self.solve(first, second), int_oracle(first, second))

    def test_long_revisions_beyond_32_bits(self):
        # Outside the stated guarantee on purpose: the comparison must not rely
        # on parsing into a fixed-width integer.
        long_nines = '9' * 100
        self.assertEqual(self.solve('1.' + long_nines, '1.' + long_nines), 0)
        self.assertEqual(self.solve('1.' + long_nines, '1.' + '9' * 99 + '8'), 1)
        self.assertEqual(self.solve('1.' + '0' * 100 + '5', '1.5'), 0)
        self.assertEqual(self.solve('1.' + '0' * 100 + '5', '1.6'), -1)
        self.assertEqual(self.solve('2', '1.' + long_nines), 1)
        self.assertEqual(self.solve('1.' + '1' * 400, '1.' + '1' * 399 + '2'), -1)

    def test_constraint_sized(self):
        # 500 characters is the constraint maximum for each version string.
        many_parts = '.'.join(['1'] * 249)
        self.assertLessEqual(len(many_parts), 500)
        self.assertEqual(self.solve(many_parts, many_parts), 0)
        self.assertEqual(len(many_parts.split('.')), 249)

        longer = many_parts + '.2'
        self.assertEqual(self.solve(many_parts, longer), -1)
        self.assertEqual(self.solve(longer, many_parts), 1)

        trailing_zeros = many_parts + '.0'
        self.assertLessEqual(len(trailing_zeros), 500)
        self.assertEqual(self.solve(many_parts, trailing_zeros), 0)

        big_revisions = '.'.join([str(2 ** 31 - 1)] * 41)
        self.assertLessEqual(len(big_revisions), 500)
        self.assertEqual(self.solve(big_revisions, big_revisions), 0)
        self.assertEqual(self.solve(big_revisions, big_revisions + '.1'), -1)


if __name__ == '__main__':
    unittest.main()
