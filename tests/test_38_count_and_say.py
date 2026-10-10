import re
import unittest

from _loader import load_solution

Solution = load_solution('38-count-and-say.py').Solution


def brute_force(n: int) -> str:
    """Independent RLE using a regex over maximal digit runs."""
    term = '1'
    for _ in range(n - 1):
        # finditer is required: findall would return only the captured digit,
        # not the whole run.
        term = ''.join(
            f'{match.end() - match.start()}{match.group(1)}'
            for match in re.finditer(r'(\d)\1*', term)
        )
    return term


class CountAndSayTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().countAndSay

    def test_official_examples(self):
        self.assertEqual(self.solve(1), '1')
        self.assertEqual(self.solve(4), '1211')

    def test_first_terms(self):
        expected = ['1', '11', '21', '1211', '111221', '312211']
        for n, term in enumerate(expected, start=1):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), term)

    def test_only_digits_one_two_and_three_appear(self):
        term = self.solve(30)
        self.assertTrue(set(term) <= {'1', '2', '3'})

    def test_exhaustive_against_brute_force(self):
        for n in range(1, 31):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), brute_force(n))

    def test_length_grows_as_expected(self):
        # The sequence is Conway's; the length ratio settles near 1.3036.
        lengths = [len(self.solve(n)) for n in range(1, 31)]
        self.assertEqual(lengths[0], 1)
        self.assertEqual(lengths, [len(brute_force(n)) for n in range(1, 31)])
        self.assertGreater(lengths[29] / lengths[28], 1.2)


if __name__ == '__main__':
    unittest.main()
