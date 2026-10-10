import itertools
import unittest

from _loader import load_solution

Solution = load_solution('60-permutation-sequence.py').Solution


def brute_force(n: int, k: int) -> str:
    """List the permutations in lexicographic order and index into them."""
    ordered = sorted(''.join(p) for p in itertools.permutations('123456789'[:n]))
    return ordered[k - 1]


class PermutationSequenceTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().getPermutation

    def test_official_examples(self):
        self.assertEqual(self.solve(3, 3), '213')
        self.assertEqual(self.solve(4, 9), '2314')
        self.assertEqual(self.solve(3, 1), '123')

    def test_first_and_last_permutation(self):
        self.assertEqual(self.solve(4, 1), '1234')
        self.assertEqual(self.solve(4, 24), '4321')

    def test_single_digit(self):
        self.assertEqual(self.solve(1, 1), '1')

    def test_two_digits(self):
        self.assertEqual(self.solve(2, 1), '12')
        self.assertEqual(self.solve(2, 2), '21')

    def test_result_is_a_permutation_of_1_to_n(self):
        for n in range(1, 10):
            with self.subTest(n=n):
                result = self.solve(n, 1)
                self.assertEqual(sorted(result), sorted('123456789'[:n]))

    def test_maximum_n_boundaries(self):
        self.assertEqual(self.solve(9, 1), '123456789')
        self.assertEqual(self.solve(9, 362880), '987654321')
        self.assertEqual(self.solve(9, 362880 - 1), '987654312')

    def test_exhaustive_small_cases(self):
        for n in range(1, 7):
            for k in range(1, len(list(itertools.permutations(range(n)))) + 1):
                with self.subTest(n=n, k=k):
                    self.assertEqual(self.solve(n, k), brute_force(n, k))

    def test_exhaustive_against_brute_force_for_n_seven(self):
        for k in (1, 2, 500, 5039, 5040):
            with self.subTest(k=k):
                self.assertEqual(self.solve(7, k), brute_force(7, k))


if __name__ == '__main__':
    unittest.main()
