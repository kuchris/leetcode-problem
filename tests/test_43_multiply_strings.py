import random
import unittest

from _loader import load_solution

Solution = load_solution('43-multiply-strings.py').Solution


class MultiplyStringsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().multiply

    def test_official_examples(self):
        self.assertEqual(self.solve('2', '3'), '6')
        self.assertEqual(self.solve('123', '456'), '56088')

    def test_zero_operands(self):
        self.assertEqual(self.solve('0', '0'), '0')
        self.assertEqual(self.solve('0', '12345'), '0')
        self.assertEqual(self.solve('999', '0'), '0')

    def test_identity(self):
        self.assertEqual(self.solve('1', '1'), '1')
        self.assertEqual(self.solve('12345', '1'), '12345')
        self.assertEqual(self.solve('1', '99999'), '99999')

    def test_single_digits(self):
        for a in range(10):
            for b in range(10):
                with self.subTest(a=a, b=b):
                    self.assertEqual(self.solve(str(a), str(b)), str(a * b))

    def test_no_leading_zero_in_the_result(self):
        result = self.solve('100', '100')
        self.assertEqual(result, '10000')
        self.assertFalse(result.startswith('0'))

    def test_maximum_length_operands(self):
        first = '9' * 200
        second = '9' * 200
        expected = str(int(first) * int(second))
        self.assertEqual(self.solve(first, second), expected)

    def test_maximum_length_with_zeros_inside(self):
        first = '1' + '0' * 198 + '1'
        second = '9' * 200
        self.assertEqual(self.solve(first, second), str(int(first) * int(second)))

    def test_exhaustive_small_operands(self):
        for a in range(0, 120):
            for b in range(0, 120, 7):
                with self.subTest(a=a, b=b):
                    self.assertEqual(self.solve(str(a), str(b)), str(a * b))

    def test_randomised_large_operands(self):
        rng = random.Random(43)
        for _ in range(60):
            first = ''.join(rng.choice('0123456789') for _ in range(rng.randint(1, 200))).lstrip('0') or '0'
            second = ''.join(rng.choice('0123456789') for _ in range(rng.randint(1, 200))).lstrip('0') or '0'
            with self.subTest(lengths=(len(first), len(second))):
                self.assertEqual(self.solve(first, second), str(int(first) * int(second)))


if __name__ == '__main__':
    unittest.main()
