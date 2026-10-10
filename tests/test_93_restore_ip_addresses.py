"""Tests for 93. Restore IP Addresses.

Oracle: re-split the string at every triple of cut positions with
``itertools.combinations`` and keep the splits whose four parts are legal
octets. The solution backtracks octet by octet with pruning, so the two agree
only if the octet rules and the pruning are both right.

Results are order-insensitive on LeetCode, so every comparison sorts.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('93-restore-ip-addresses.py').Solution


def is_octet(part: str) -> bool:
    if not 1 <= len(part) <= 3:
        return False
    if part[0] == '0':
        return len(part) == 1
    return int(part) <= 255


def brute_force(s: str) -> list[str]:
    """Every legal four-part split of s, found by trying all cut positions."""
    n = len(s)
    addresses = []
    for cuts in itertools.combinations(range(1, n), 3):
        boundaries = (*cuts, n)
        parts = []
        previous = 0
        for cut in boundaries:
            parts.append(s[previous:cut])
            previous = cut
        if all(is_octet(part) for part in parts):
            addresses.append('.'.join(parts))
    return addresses


def digits_of_length(length, alphabet='0125'):
    for combination in itertools.product(alphabet, repeat=length):
        yield ''.join(combination)


class RestoreIpAddressesTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().restoreIpAddresses

    def check(self, s):
        return sorted(self.solve(s))

    def test_official_examples(self):
        self.assertEqual(self.check('25525511135'), ['255.255.11.135', '255.255.111.35'])
        self.assertEqual(self.check('0000'), ['0.0.0.0'])
        self.assertEqual(
            self.check('101023'),
            ['1.0.10.23', '1.0.102.3', '10.1.0.23', '10.10.2.3', '101.0.2.3'],
        )

    def test_leading_zero_examples(self):
        # "010010" is the classic leading-zero case.
        self.assertEqual(self.check('010010'), ['0.10.0.10', '0.100.1.0'])
        self.assertEqual(self.check('01000'), ['0.10.0.0'])
        self.assertEqual(self.check('1000'), ['1.0.0.0'])

    def test_length_outside_four_to_twelve(self):
        self.assertEqual(self.check(''), [])
        self.assertEqual(self.check('1'), [])
        self.assertEqual(self.check('123'), [])
        self.assertEqual(self.check('1234567890123'), [])  # 13 digits
        self.assertEqual(self.check('0' * 13), [])
        self.assertEqual(self.check('0' * 20), [])

    def test_octet_bounds(self):
        self.assertEqual(self.check('1111'), ['1.1.1.1'])
        self.assertEqual(self.check('255255255255'), ['255.255.255.255'])
        # 256 is never a legal octet.
        self.assertEqual(self.check('256256256256'), [])
        # Twelve ones only fit as four 3-digit octets.
        self.assertEqual(self.check('111111111111'), ['111.111.111.111'])

    def test_all_zeroes(self):
        self.assertEqual(self.check('0000'), ['0.0.0.0'])
        self.assertEqual(self.check('00000'), [])
        self.assertEqual(self.check('000000000000'), [])

    def test_exhaustive_small_cases(self):
        for length in range(1, 7):
            for s in digits_of_length(length):
                with self.subTest(s=s):
                    self.assertEqual(self.check(s), sorted(brute_force(s)))

    def test_random_long_cases(self):
        rng = random.Random(931)
        for _ in range(300):
            length = rng.randint(1, 20)
            s = ''.join(rng.choice('0123456789') for _ in range(length))
            with self.subTest(s=s):
                self.assertEqual(self.check(s), sorted(brute_force(s)))

    def test_random_dot_free_case(self):
        # A string built by gluing four legal octets always has at least one answer.
        rng = random.Random(932)
        for _ in range(200):
            octets = [str(rng.choice([0, 1, 9, 10, 99, 100, 200, 255])) for _ in range(4)]
            s = ''.join(octets)
            with self.subTest(s=s):
                self.assertIn('.'.join(octets), self.solve(s))
                self.assertEqual(self.check(s), sorted(brute_force(s)))

    def test_constraint_sized(self):
        # 20 digits is the constraint maximum.
        cases = [
            '1' * 20,
            '25525525525525525525',
            '10102310102310102310',
            '11111111111111111111',
            '99999999999999999999',
            '00001111222233334444',
        ]
        for s in cases:
            with self.subTest(s=s):
                self.assertEqual(len(s), 20)
                self.assertEqual(self.check(s), sorted(brute_force(s)))

        # 12 digits is where the answer count peaks (the four octets need at
        # least one digit each and can hold at most twelve).
        s = '123451234512'
        self.assertEqual(self.check(s), sorted(brute_force(s)))


if __name__ == '__main__':
    unittest.main()
