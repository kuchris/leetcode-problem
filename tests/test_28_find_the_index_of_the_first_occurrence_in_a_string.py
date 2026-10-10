import itertools
import unittest

from _loader import load_solution

Solution = load_solution('28-find-the-index-of-the-first-occurrence-in-a-string.py').Solution


def brute_force(haystack: str, needle: str) -> int:
    """Try every alignment."""
    if not needle:
        return 0
    for start in range(len(haystack) - len(needle) + 1):
        if haystack[start:start + len(needle)] == needle:
            return start
    return -1


class StrStrTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().strStr

    def test_official_examples(self):
        self.assertEqual(self.solve('sadbutsad', 'sad'), 0)
        self.assertEqual(self.solve('leetcode', 'leeto'), -1)

    def test_empty_needle(self):
        self.assertEqual(self.solve('abc', ''), 0)

    def test_needle_longer_than_haystack(self):
        self.assertEqual(self.solve('ab', 'abc'), -1)

    def test_needle_equals_haystack(self):
        self.assertEqual(self.solve('abc', 'abc'), 0)

    def test_overlapping_matches_report_the_first(self):
        self.assertEqual(self.solve('aaa', 'aa'), 0)
        self.assertEqual(self.solve('aaaa', 'aaa'), 0)

    def test_match_at_the_end(self):
        self.assertEqual(self.solve('ababc', 'abc'), 2)

    def test_worst_case_for_a_naive_scan(self):
        # KMP must stay linear here; a naive scan would be O(n * m).
        haystack = 'a' * 10000
        self.assertEqual(self.solve(haystack, 'a' * 9999 + 'b'), -1)
        self.assertEqual(self.solve(haystack, 'a' * 10000), 0)
        self.assertEqual(self.solve('ab' * 5000, 'ab' * 4999 + 'ba'), -1)

    def test_exhaustive_small_cases(self):
        strings = ['']
        for size in range(1, 6):
            strings += [''.join(c) for c in itertools.product('ab', repeat=size)]
        for haystack in strings:
            for needle in strings:
                with self.subTest(haystack=haystack, needle=needle):
                    self.assertEqual(
                        self.solve(haystack, needle), brute_force(haystack, needle)
                    )


if __name__ == '__main__':
    unittest.main()
