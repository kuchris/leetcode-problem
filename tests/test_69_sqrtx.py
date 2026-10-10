import math
import random
import unittest

from _loader import load_solution

Solution = load_solution('69-sqrtx.py').Solution


class SqrtXTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().mySqrt

    def test_official_examples(self):
        self.assertEqual(self.solve(4), 2)
        self.assertEqual(self.solve(8), 2)

    def test_zero_and_one(self):
        self.assertEqual(self.solve(0), 0)
        self.assertEqual(self.solve(1), 1)

    def test_perfect_squares(self):
        for root in range(0, 100):
            with self.subTest(root=root):
                self.assertEqual(self.solve(root * root), root)

    def test_just_below_and_above_a_perfect_square(self):
        for root in range(1, 100):
            square = root * root
            with self.subTest(root=root):
                self.assertEqual(self.solve(square - 1), root - 1)
                self.assertEqual(self.solve(square + 1), root)

    def test_maximum_value(self):
        limit = 2 ** 31 - 1
        self.assertEqual(self.solve(limit), math.isqrt(limit))
        self.assertEqual(self.solve(limit - 1), math.isqrt(limit - 1))

    def test_result_is_the_floor_of_the_square_root(self):
        rng = random.Random(69)
        for _ in range(300):
            x = rng.randint(0, 2 ** 31 - 1)
            with self.subTest(x=x):
                result = self.solve(x)
                self.assertEqual(result, math.isqrt(x))
                self.assertLessEqual(result * result, x)
                self.assertGreater((result + 1) * (result + 1), x)

    def test_exhaustive_small_values(self):
        for x in range(0, 2000):
            with self.subTest(x=x):
                self.assertEqual(self.solve(x), math.isqrt(x))

    def test_all_values_around_every_small_square_root(self):
        for root in range(1, 500):
            for x in range(root * root - 2, root * root + 3):
                if x < 0:
                    continue
                with self.subTest(x=x):
                    self.assertEqual(self.solve(x), math.isqrt(x))


if __name__ == '__main__':
    unittest.main()
