import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('66-plus-one.py').Solution


def brute_force(digits: list[int]) -> list[int]:
    """Go through the integer value and split it back into digits."""
    value = int(''.join(str(d) for d in digits)) + 1
    return [int(char) for char in str(value)]


class PlusOneTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().plusOne

    def apply(self, digits):
        return self.solve(list(digits))

    def test_official_examples(self):
        self.assertEqual(self.apply([1, 2, 3]), [1, 2, 4])
        self.assertEqual(self.apply([4, 3, 2, 1]), [4, 3, 2, 2])
        self.assertEqual(self.apply([9]), [1, 0])

    def test_single_digit(self):
        for digit in range(9):
            with self.subTest(digit=digit):
                self.assertEqual(self.apply([digit]), [digit + 1])
        self.assertEqual(self.apply([9]), [1, 0])

    def test_carry_propagation(self):
        self.assertEqual(self.apply([1, 9]), [2, 0])
        self.assertEqual(self.apply([1, 9, 9]), [2, 0, 0])
        self.assertEqual(self.apply([9, 9, 9]), [1, 0, 0, 0])

    def test_no_carry_needed(self):
        self.assertEqual(self.apply([1, 2, 3, 4]), [1, 2, 3, 5])

    def test_maximum_length(self):
        self.assertEqual(self.apply([9] * 100), [1] + [0] * 100)
        digits = [9] * 99 + [8]
        self.assertEqual(self.apply(digits), [9] * 99 + [9])

    def test_exhaustive_small_cases(self):
        for size in range(1, 6):
            for digits in itertools.product(range(10), repeat=size):
                if digits[0] == 0:
                    continue  # no leading zeros per the statement
                with self.subTest(digits=digits):
                    self.assertEqual(self.apply(digits), brute_force(list(digits)))

    def test_randomised_cases(self):
        rng = random.Random(66)
        for _ in range(100):
            size = rng.randint(1, 20)
            digits = [rng.randint(1, 9)] + [rng.randint(0, 9) for _ in range(size - 1)]
            with self.subTest(digits=digits):
                self.assertEqual(self.apply(digits), brute_force(digits))


if __name__ == '__main__':
    unittest.main()
