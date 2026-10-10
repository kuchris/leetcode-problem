import itertools
import unittest

from _loader import load_solution

Solution = load_solution('67-add-binary.py').Solution


def brute_force(a: str, b: str) -> str:
    """Independent oracle: Python's own integer and binary conversion."""
    return bin(int(a, 2) + int(b, 2))[2:]


class AddBinaryTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().addBinary

    def test_official_examples(self):
        self.assertEqual(self.solve('11', '1'), '100')
        self.assertEqual(self.solve('1010', '1011'), '10101')

    def test_zero_operand(self):
        self.assertEqual(self.solve('0', '0'), '0')
        self.assertEqual(self.solve('0', '1'), '1')
        self.assertEqual(self.solve('1', '0'), '1')

    def test_carry_ripples_across_every_digit(self):
        self.assertEqual(self.solve('1111', '1'), '10000')
        self.assertEqual(self.solve('1' * 100, '1'), '1' + '0' * 100)

    def test_very_different_lengths(self):
        self.assertEqual(self.solve('1', '1' * 50), '1' + '0' * 50)

    def test_maximum_length(self):
        a = '1' * 10000
        b = '1' * 9999
        self.assertEqual(self.solve(a, b), brute_force(a, b))

    def test_exhaustive_small_cases(self):
        values = [format(n, 'b') for n in range(64)]
        for a in values:
            for b in values:
                with self.subTest(a=a, b=b):
                    self.assertEqual(self.solve(a, b), brute_force(a, b))

    def test_exhaustive_all_bit_strings(self):
        # The statement guarantees no leading zeros other than "0" itself, so
        # "01" and "00" are not legal inputs and are excluded here.
        strings = ['0']
        for size in range(1, 7):
            strings += [
                ''.join(bits)
                for bits in itertools.product('01', repeat=size)
                if bits[0] == '1'
            ]
        for a in strings:
            for b in strings:
                with self.subTest(a=a, b=b):
                    self.assertEqual(self.solve(a, b), brute_force(a, b))


if __name__ == '__main__':
    unittest.main()
