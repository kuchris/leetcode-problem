"""Tests for 191. Number of 1 Bits.

Oracles:

  - `bin(n).count('1')` -- the string form of the number, sharing no arithmetic
    with the solution;
  - `popcount_by_shifts`, a fixed 32-position shift loop -- the approach the
    follow-up rules out, used here as a second, structurally different way to
    reach the same answer.

`Probe` pins the follow-up. It wraps the argument so that every bitwise AND the
algorithm performs is counted, and it deliberately does not implement the
operations a built-in bit count needs (`bin`, `int.bit_count`, `__index__`), so a
regression to `bin(n).count('1')` or to a fixed 32-iteration loop fails loudly
instead of passing silently.
"""

import itertools
import random
import unittest

from _loader import SOLUTIONS_DIR, load_solution

Solution = load_solution('191-number-of-1-bits.py').Solution

UPPER = 2 ** 31 - 1


def popcount_by_shifts(n: int) -> int:
    count = 0
    for position in range(31):
        count += (n >> position) & 1
    return count


class Probe:
    """Wraps an int, counts every `&`, and supports only what the loop needs.

    `n & (n - 1)` calls `__and__` once per iteration and rebinds the result, so a
    Kernighan loop is counted exactly popcount times. A shift loop would call
    `__rshift__`/`__and__` 31 times, and a built-in bit count would raise,
    because `bin()` and `int.bit_count()` are not reachable from this object.
    """

    def __init__(self, value: int, counter: list):
        self.value = value
        self.counter = counter

    def __sub__(self, other):
        return Probe(self.value - other, self.counter)

    def __and__(self, other):
        self.counter[0] += 1
        other_value = other.value if isinstance(other, Probe) else other
        return Probe(self.value & other_value, self.counter)

    def __rshift__(self, other):
        return Probe(self.value >> other, self.counter)

    def __bool__(self):
        return self.value != 0


class NumberOfOneBitsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().hammingWeight

    def assert_popcount(self, n: int) -> int:
        expected = bin(n).count('1')
        result = self.solve(n)
        self.assertEqual(result, expected, f'n = {n}')
        self.assertEqual(expected, popcount_by_shifts(n), f'n = {n}')
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve(11), 3)
        self.assertEqual(self.solve(128), 1)
        self.assertEqual(self.solve(2147483645), 30)

    def test_constraint_boundaries(self):
        self.assertEqual(self.solve(1), 1)  # smallest allowed input
        self.assertEqual(self.solve(UPPER), 31)  # largest allowed input
        self.assertEqual(self.solve(UPPER - 1), 30)
        self.assertEqual(self.solve(2 ** 30), 1)
        self.assertEqual(self.solve(2 ** 30 + 1), 2)
        self.assertEqual(bin(UPPER).count('1'), 31)

    def test_powers_of_two_have_one_bit(self):
        for exponent in range(31):
            with self.subTest(exponent=exponent):
                self.assertEqual(self.solve(2 ** exponent), 1)

    def test_one_less_than_a_power_of_two(self):
        for exponent in range(2, 32):
            with self.subTest(exponent=exponent):
                self.assertEqual(self.solve(2 ** exponent - 1), exponent)

    def test_exhaustive_low_sixteen_bits(self):
        # Every value with 1 <= n <= 2^16 - 1, compared in bulk to avoid one
        # subTest per value.
        values = list(range(1, 1 << 16))
        self.assertEqual(
            [self.solve(value) for value in values],
            [bin(value).count('1') for value in values],
        )

    def test_exhaustive_high_windows(self):
        for top in (2 ** 16 - 1, 2 ** 24 - 1, 2 ** 30, UPPER):
            window = [top - delta for delta in range(4096)]
            with self.subTest(top=top):
                self.assertEqual(
                    [self.solve(value) for value in window],
                    [bin(value).count('1') for value in window],
                )

    def test_exhaustive_patterns_with_few_bits(self):
        # Every 16-bit pattern with at most four set bits: the answer is known by
        # construction, and these are the values that make a fixed-width loop
        # look correct (its cost is 32 steps regardless of the answer).
        for count in range(5):
            for positions in itertools.combinations(range(16), count):
                n = sum(1 << position for position in positions)
                if n == 0:
                    continue  # n >= 1 is guaranteed
                with self.subTest(n=n):
                    self.assertEqual(self.solve(n), count)

    def test_randomised_thirty_two_bit_values(self):
        rng = random.Random(1910)
        for _ in range(3000):
            n = rng.randint(1, UPPER)
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), bin(n).count('1'))

    def test_randomised_dense_and_sparse_values(self):
        rng = random.Random(1911)
        for bits in (1, 2, 3, 8, 16, 24, 31):
            for _ in range(50):
                positions = rng.sample(range(31), bits)
                n = sum(1 << position for position in positions)
                with self.subTest(n=n):
                    self.assertEqual(self.solve(n), bits)

    def test_iterations_equal_popcount(self):
        # The follow-up test: the loop must run once per set bit, not once per
        # bit position. A single-bit value must therefore cost exactly one step.
        rng = random.Random(1912)
        cases = [1, 2, 8, 2 ** 30, UPPER, UPPER - 1, 0b1010101010101010]
        cases += [rng.randint(1, UPPER) for _ in range(200)]
        for n in cases:
            counter = [0]
            result = self.solve(Probe(n, counter))
            expected = bin(n).count('1')
            with self.subTest(n=n):
                self.assertEqual(result, expected)
                self.assertEqual(counter[0], expected, 'the loop must be O(popcount)')

        # Specific witness: 2^30 has one set bit, so a 32-step loop would show 31
        # steps too many.
        counter = [0]
        self.assertEqual(self.solve(Probe(2 ** 30, counter)), 1)
        self.assertEqual(counter[0], 1)
        counter = [0]
        self.assertEqual(self.solve(Probe(UPPER, counter)), 31)
        self.assertEqual(counter[0], 31)

    def test_follow_up_avoids_builtin_bit_count(self):
        source = (SOLUTIONS_DIR / '191-number-of-1-bits.py').read_text(encoding='utf-8')
        self.assertNotIn('bit_count', source, 'the follow-up rules out int.bit_count()')
        self.assertNotIn('bin(', source, 'the follow-up rules out bin()/format() bit counting')

    def test_constraint_sized(self):
        # The largest allowed input, and values that are dense or sparse near it.
        self.assertEqual(self.solve(UPPER), 31)
        self.assertEqual(self.solve(UPPER >> 1), 30)
        biggest_single_bit = 1 << 30
        self.assertEqual(self.solve(biggest_single_bit), 1)
        self.assertEqual(self.solve(0b1 << 30 | 0b1), 2)
        self.assertEqual(self.solve(0x55555555), 16)  # 1431655765 < 2^31
        self.assertEqual(self.solve(0x7FFFFFFE), 30)


if __name__ == '__main__':
    unittest.main()
