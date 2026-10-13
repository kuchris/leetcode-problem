"""Tests for 190. Reverse Bits.

Oracles:
  - ``string_oracle``: ``int(format(n, '032b')[::-1], 2)`` — the fixed 32-bit
    width is written out explicitly, so leading zeros of the input become
    trailing zeros of the output.
  - ``position_oracle``: bit i of n is placed at bit 31 - i, an explicit index
    mapping with no strings and no shifting loop.

The statement's constraint says n is even. Reversal is defined for every 32-bit
value, so odd inputs live in one clearly labelled case outside that guarantee
rather than inside the sweeps that respect it.

Sweeps: every even n below 2^16 against both oracles, plus all 2^16 values for
the structural properties.
"""

import random
import unittest

from _loader import load_solution

Solution = load_solution('190-reverse-bits.py').Solution

BITS = 32
MAX_INPUT = 2 ** 31 - 2      # the largest value the constraint allows
MODULUS = 2 ** 32


def string_oracle(n: int) -> int:
    return int(format(n, '032b')[::-1], 2)


def position_oracle(n: int) -> int:
    return sum(((n >> index) & 1) << (BITS - 1 - index) for index in range(BITS))


class ReverseBitsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().reverseBits

    def check(self, n):
        result = self.solve(n)
        self.assertEqual(result, string_oracle(n))
        self.assertEqual(result, position_oracle(n))
        self.assertLess(result, MODULUS)
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve(43261596), 964176192)
        self.assertEqual(self.solve(2147483644), 1073741822)
        self.check(43261596)
        self.check(2147483644)

    def test_zero(self):
        self.assertEqual(self.solve(0), 0)
        self.assertEqual(self.solve(0), string_oracle(0))

    def test_single_bits(self):
        # Bit i moves to bit 31 - i; bit 0 is the odd input, handled below.
        for index in range(1, BITS):
            value = 1 << index
            with self.subTest(index=index):
                self.assertEqual(self.solve(value), 1 << (BITS - 1 - index))

    def test_leading_zeros_become_trailing_zeros(self):
        # 2 = ...0010 reverses to a 1 at the top and 30 trailing zeros.
        self.assertEqual(self.solve(2), 1 << 30)
        self.assertEqual(format(self.solve(2), '032b'), '0' + '1' + '0' * 30)
        # The high half of a small number lands in the low half.
        self.assertEqual(self.solve(6), (1 << 29) | (1 << 30))
        self.check(6)

    def test_extremes_allowed_by_the_constraint(self):
        # 2^31 - 2 is 0111...1110, a symmetric pattern, so it reverses to
        # itself; 2^31 - 4 (= the official 2147483644) reverses to 1073741822.
        self.assertEqual(string_oracle(MAX_INPUT), MAX_INPUT)
        self.assertEqual(self.solve(MAX_INPUT), MAX_INPUT)
        self.assertEqual(self.solve(MAX_INPUT - 2), 1073741822)
        self.assertEqual(self.solve(MAX_INPUT - 2), string_oracle(MAX_INPUT - 2))
        self.assertEqual(self.solve(1 << 30), 2)
        self.assertEqual(self.solve((1 << 31) - 4), string_oracle((1 << 31) - 4))
        self.check(MAX_INPUT)
        self.check(1 << 30)

    def test_every_even_value_below_2_to_the_16(self):
        for n in range(0, 1 << 16, 2):
            with self.subTest(n=n):
                self.check(n)

    def test_every_value_below_2_to_the_16_keeps_the_structure(self):
        # All 2^16 values, including the odd ones, for the width properties.
        for n in range(1 << 16):
            with self.subTest(n=n):
                result = self.solve(n)
                self.assertEqual(result, string_oracle(n))
                self.assertLess(result, MODULUS)
                self.assertEqual(self.solve(result), n)   # involution on 32 bits

    def test_random_values_are_involutions(self):
        rng = random.Random(1900)
        for _ in range(2000):
            n = rng.randrange(0, MODULUS)
            with self.subTest(n=n):
                self.check(n)
                self.assertEqual(self.solve(self.solve(n)), n)

    def test_random_even_values_within_the_constraint(self):
        rng = random.Random(1901)
        for _ in range(2000):
            n = rng.randrange(0, MAX_INPUT // 2 + 1) * 2
            with self.subTest(n=n):
                self.check(n)

    def test_odd_values_outside_the_stated_guarantee(self):
        # The constraint says n is even; the operation is still well defined.
        self.assertEqual(self.solve(1), 1 << 31)
        self.assertEqual(self.solve(3), (1 << 31) | (1 << 30))
        for n in range(1, 1 << 12, 2):
            with self.subTest(n=n):
                self.check(n)
        rng = random.Random(1902)
        for _ in range(500):
            n = rng.randrange(0, MODULUS) | 1
            with self.subTest(n=n):
                self.check(n)


if __name__ == '__main__':
    unittest.main()
