"""Tests for 89. Gray Code.

Any valid sequence is accepted, so the oracle is structural: an independent
reflect-and-prefix construction (the definition of a reflected Gray code) plus
explicit property checks -- length 2^n, starts at 0, in range, all distinct, and
every adjacent pair (including the wrap-around pair) differing in exactly one
bit. Bit counting is done twice, with int.bit_count and with bin().count('1'),
so a single flawed popcount cannot make both checks agree by accident.
"""

import unittest

from _loader import load_solution

Solution = load_solution('89-gray-code.py').Solution


def reflected_gray(n: int) -> list[int]:
    """Reflect-and-prefix construction: G(n) = G(n-1) followed by its mirror."""
    result = [0]
    for bit in range(n):
        result += [value | (1 << bit) for value in reversed(result)]
    return result


def structural_problem(sequence: list[int], n: int) -> str | None:
    """Return a description of the first violated property, or None."""
    size = 1 << n
    if len(sequence) != size:
        return f'length {len(sequence)} != {size}'
    if sequence[0] != 0:
        return f'first element is {sequence[0]}, not 0'
    if len(set(sequence)) != size:
        return 'values repeat'
    for value in sequence:
        if not 0 <= value < size:
            return f'{value} is outside [0, {size - 1}]'
    for i in range(size):
        a = sequence[i]
        b = sequence[(i + 1) % size]
        if a.bit_count() + b.bit_count() - 2 * (a & b).bit_count() != 1:
            return f'neighbours {a} and {b} differ by more than one bit'
        if bin(a ^ b).count('1') != 1:
            return f'popcount via bin() disagrees for {a} and {b}'
    return None


class GrayCodeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().grayCode

    def test_official_examples(self):
        self.assertEqual(self.solve(2), [0, 1, 3, 2])
        self.assertEqual(self.solve(1), [0, 1])

    def test_smallest_n(self):
        result = self.solve(1)
        self.assertEqual(result, [0, 1])
        self.assertEqual(result[0] ^ result[1], 1)

    def test_matches_the_reflected_construction(self):
        for n in range(1, 17):
            with self.subTest(n=n):
                self.assertEqual(self.solve(n), reflected_gray(n))

    def test_properties_hold(self):
        for n in range(1, 13):
            with self.subTest(n=n):
                self.assertIsNone(structural_problem(self.solve(n), n))

    def test_exhaustive_small_cases(self):
        # Every n in the constraint range, checked against both oracles.
        for n in range(1, 17):
            sequence = self.solve(n)
            with self.subTest(n=n):
                self.assertIsNone(structural_problem(sequence, n))
                self.assertEqual(sequence, reflected_gray(n))

    def test_first_and_last_differ_by_one_bit(self):
        for n in range(1, 15):
            sequence = self.solve(n)
            with self.subTest(n=n):
                self.assertEqual(bin(sequence[0] ^ sequence[-1]).count('1'), 1)

    def test_constraint_sized(self):
        n = 16
        sequence = self.solve(n)
        self.assertEqual(len(sequence), 65536)
        self.assertEqual(len(set(sequence)), 65536)
        self.assertEqual(sequence, reflected_gray(n))
        self.assertIsNone(structural_problem(sequence, n))

        # Spot-check the structure of the two ends of the sequence.
        self.assertEqual(sequence[:8], [0, 1, 3, 2, 6, 7, 5, 4])
        self.assertEqual(sequence[-1], 1 << (n - 1))
        self.assertEqual(sequence[0] ^ sequence[-1], 1 << (n - 1))


if __name__ == '__main__':
    unittest.main()
