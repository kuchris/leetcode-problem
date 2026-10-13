"""Tests for 166. Fraction to Recurring Decimal.

Three independent checks:

  - round trip: the returned string is parsed back into an exact Fraction
    (integer part, transient digits over a power of ten, repeating block over
    a power of ten times 10^len(block) - 1) and compared with
    Fraction(numerator, denominator). This never repeats the division algorithm;
  - number theory: a second expansion is derived from the reduced denominator by
    stripping its factors of 2 and 5 (which fixes the transient length as their
    maximum) and taking the multiplicative order of 10 modulo what remains (which
    fixes the period). The digits come from one scaled integer division, not from
    a digit-by-digit loop;
  - the period is asserted to be primitive (not a repetition of a shorter
    block), which pins the parenthesised form rather than just the value.

Every case also checks the statement's structural rules: no decimal point for
integer results, no parentheses for terminating expansions, and a zero numerator
never printing a sign.
"""

import itertools
import math
import random
import unittest
from fractions import Fraction

from _loader import load_solution

Solution = load_solution('166-fraction-to-recurring-decimal.py').Solution


def multiplicative_order(base: int, modulus: int, limit: int = 2 * 10 ** 4) -> int:
    """Smallest k >= 1 with base ** k % modulus == 1 (base coprime to modulus).

    The search is linear in the order, so it gives up after `limit` steps: a
    modulus with a longer period cannot appear in a legal input, because the
    statement guarantees the printed answer is shorter than 10^4 characters. The
    cap keeps the oracle from grinding on an illegal input while still accepting
    moduli like 999999, whose period is only 6.
    """
    value = base % modulus
    order = 1
    while value != 1:
        value = value * base % modulus
        order += 1
        if order > limit:
            raise AssertionError('period exceeds the statement length guarantee')
    return order


def theoretical_expansion(numerator: int, denominator: int) -> str:
    """The expansion from the 2/5 split and the order of 10 modulo the rest."""
    if numerator == 0:
        return '0'
    sign = '-' if (numerator < 0) != (denominator < 0) else ''
    n, reduced = abs(numerator), abs(denominator)
    divisor = math.gcd(n, reduced)
    n, reduced = n // divisor, reduced // divisor
    whole, remainder = divmod(n, reduced)

    coprime = reduced
    twos = fives = 0
    while coprime % 2 == 0:
        coprime //= 2
        twos += 1
    while coprime % 5 == 0:
        coprime //= 5
        fives += 1

    transient = max(twos, fives)
    period = 0 if coprime == 1 else multiplicative_order(10, coprime)

    total = transient + period
    if total == 0:
        return sign + str(whole)

    scaled = remainder * 10 ** total
    digits = str(scaled // reduced).rjust(total, '0')
    if period == 0:
        return sign + str(whole) + '.' + digits
    return sign + str(whole) + '.' + digits[:transient] + '(' + digits[transient:] + ')'


def parse_expansion(text: str) -> Fraction:
    """Read the answer format back into an exact rational."""
    sign = 1
    if text.startswith('-'):
        sign = -1
        text = text[1:]

    if '.' not in text:
        return Fraction(sign * int(text))

    whole, fraction = text.split('.')
    block = ''
    if '(' in fraction:
        prefix, rest = fraction.split('(')
        if not rest.endswith(')'):
            raise AssertionError(f'malformed parenthesis in {text!r}')
        block = rest[:-1]
        if '(' in block or ')' in block:
            raise AssertionError(f'nested parenthesis in {text!r}')
    else:
        prefix = fraction

    value = Fraction(int(whole)) if whole else Fraction(0)
    if prefix:
        value += Fraction(int(prefix), 10 ** len(prefix))
    if block:
        scale = 10 ** len(prefix) * (10 ** len(block) - 1)
        value += Fraction(int(block), scale)
    return sign * value


def block_is_primitive(block: str) -> bool:
    """True when the block is not a repetition of a shorter one."""
    for size in range(1, len(block)):
        if len(block) % size == 0 and block == block[:size] * (len(block) // size):
            return False
    return True


class FractionToRecurringDecimalTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().fractionToDecimal
        self.maxDiff = 2000

    def check(self, numerator, denominator):
        result = self.solve(numerator, denominator)
        expected = theoretical_expansion(numerator, denominator)
        self.assertEqual(result, expected)
        self.assertEqual(parse_expansion(result), Fraction(numerator, denominator))

        # Structural rules from the statement.
        self.assertNotIn('(', result.split('.')[0] if '.' in result else result)
        if '.' in result:
            self.assertTrue(result.split('.')[1])
        if '(' in result:
            block = result.split('(')[1][:-1]
            self.assertTrue(block)
            self.assertTrue(block_is_primitive(block))
            coprime = abs(denominator) // math.gcd(abs(numerator), abs(denominator))
            while coprime % 2 == 0:
                coprime //= 2
            while coprime % 5 == 0:
                coprime //= 5
            self.assertEqual(len(block), multiplicative_order(10, coprime))
        else:
            digits = abs(denominator) // math.gcd(abs(numerator), abs(denominator))
            while digits % 2 == 0:
                digits //= 2
            while digits % 5 == 0:
                digits //= 5
            self.assertEqual(digits, 1, 'a terminating expansion must have no parentheses')
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve(1, 2), '0.5')
        self.assertEqual(self.solve(2, 1), '2')
        self.assertEqual(self.solve(4, 333), '0.(012)')

    def test_zero_numerator(self):
        for denominator in (1, 2, -1, -3, 7, -999):
            with self.subTest(denominator=denominator):
                self.assertEqual(self.solve(0, denominator), '0')
                self.assertEqual(parse_expansion('0'), Fraction(0, 1))

    def test_integer_results_have_no_decimal_point(self):
        self.assertEqual(self.solve(2, 1), '2')
        self.assertEqual(self.solve(-2, 1), '-2')
        self.assertEqual(self.solve(10, 5), '2')
        self.assertEqual(self.solve(-10, 5), '-2')
        self.assertEqual(self.solve(6, 3), '2')
        self.assertEqual(self.solve(0, 5), '0')

    def test_negative_results(self):
        self.assertEqual(self.solve(-1, 2), '-0.5')
        self.assertEqual(self.solve(1, -2), '-0.5')
        self.assertEqual(self.solve(-1, -2), '0.5')
        self.assertEqual(self.solve(-7, 3), '-2.(3)')
        self.assertEqual(self.solve(7, -3), '-2.(3)')
        self.assertEqual(self.solve(-7, -3), '2.(3)')
        self.assertEqual(self.solve(-4, 333), '-0.(012)')

    def test_terminating_expansions(self):
        self.assertEqual(self.solve(1, 4), '0.25')
        self.assertEqual(self.solve(1, 8), '0.125')
        self.assertEqual(self.solve(3, 2), '1.5')
        self.assertEqual(self.solve(1, 20), '0.05')
        self.assertEqual(self.solve(7, 16), '0.4375')
        self.assertEqual(self.solve(1, 5), '0.2')

    def test_pure_repeating_expansions(self):
        self.assertEqual(self.solve(1, 3), '0.(3)')
        self.assertEqual(self.solve(2, 3), '0.(6)')
        self.assertEqual(self.solve(1, 7), '0.(142857)')
        self.assertEqual(self.solve(10, 3), '3.(3)')
        self.assertEqual(self.solve(1, 9), '0.(1)')
        self.assertEqual(self.solve(1, 11), '0.(09)')

    def test_mixed_transient_and_repeating(self):
        self.assertEqual(self.solve(1, 6), '0.1(6)')
        self.assertEqual(self.solve(5, 6), '0.8(3)')
        self.assertEqual(self.solve(1, 12), '0.08(3)')
        self.assertEqual(self.solve(1, 28), theoretical_expansion(1, 28))

    def test_exhaustive_small_cases(self):
        for numerator in range(-20, 21):
            for denominator in range(-20, 21):
                if denominator == 0:
                    continue
                with self.subTest(numerator=numerator, denominator=denominator):
                    self.check(numerator, denominator)

    def test_exhaustive_small_cases_permutations_of_signs(self):
        for numerator, denominator in itertools.product(range(1, 13), repeat=2):
            for sign_n, sign_d in itertools.product((1, -1), repeat=2):
                with self.subTest(numerator=numerator, denominator=denominator,
                                  signs=(sign_n, sign_d)):
                    self.check(sign_n * numerator, sign_d * denominator)

    def test_randomised_cases(self):
        rng = random.Random(1660)
        for _ in range(300):
            numerator = rng.randint(-10 ** 6, 10 ** 6)
            denominator = rng.choice([1, -1]) * rng.randint(1, 2000)
            with self.subTest(numerator=numerator, denominator=denominator):
                self.check(numerator, denominator)

    def test_boundary_values(self):
        # Boundary numerators and denominators, but only in combinations whose
        # expansion stays well inside the statement's length guarantee.
        self.check(-2 ** 31, 1)
        self.check(2 ** 31 - 1, 1)
        self.check(-2 ** 31, -1)
        self.check(-2 ** 31, 2)
        self.check(2 ** 31 - 1, 2)
        self.check(-2 ** 31, 5)
        self.check(-2 ** 31, -10)
        self.check(1, -2 ** 31)
        self.check(1, 2 ** 31)
        self.check(-1, 2 ** 20)
        self.check(2 ** 31 - 1, -(2 ** 16))

    def test_long_expansions(self):
        # Long but still inside the statement's "answer shorter than 10^4" bound.
        for numerator, denominator in ((1, 9973), (1, 9998), (1, 999999), (22, 7)):
            with self.subTest(denominator=denominator):
                result = self.check(numerator, denominator)
                self.assertLess(len(result), 10 ** 4)

        result = self.check(1, 2 ** 31)
        # 1 / 2^31 terminates after exactly 31 decimal digits.
        self.assertEqual(len(result.split('.')[1]), 31)
        self.assertLess(len(result), 10 ** 4)


if __name__ == '__main__':
    unittest.main()
