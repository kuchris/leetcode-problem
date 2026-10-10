"""Tests for 121. Best Time to Buy and Sell Stock.

Oracles:
  - ``brute_force``: every (buy, sell) pair with buy < sell, floored at 0 —
    the definition, no scan invariant involved.
  - ``kadane_on_deltas``: the best single trade is the maximum subarray sum of
    the day-to-day differences (a rise is exactly p[j] - p[i] telescoped), a
    deliberately different formulation used for the 10^5-day cases.
  - closed forms: a non-increasing series can never profit, a strictly rising
    one is worth exactly last - first.

Exhaustive sweep: every price series of length 1..6 over {0, 1, 2, 5}.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('121-best-time-to-buy-and-sell-stock.py').Solution

MAX_DAYS = 10 ** 5
MAX_PRICE = 10 ** 4


def brute_force(prices) -> int:
    best = 0
    for buy in range(len(prices)):
        for sell in range(buy + 1, len(prices)):
            best = max(best, prices[sell] - prices[buy])
    return best


def kadane_on_deltas(prices) -> int:
    """Maximum subarray sum of the daily differences, floored at 0."""
    best = 0
    current = 0
    for today, tomorrow in zip(prices, prices[1:]):
        current = max(0, current + tomorrow - today)
        best = max(best, current)
    return best


class BestTimeToBuyAndSellStockTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maxProfit

    def test_official_examples(self):
        self.assertEqual(self.solve([7, 1, 5, 3, 6, 4]), 5)
        self.assertEqual(self.solve([7, 6, 4, 3, 1]), 0)

    def test_single_day_cannot_trade(self):
        self.assertEqual(self.solve([0]), 0)
        self.assertEqual(self.solve([5]), 0)
        self.assertEqual(self.solve([MAX_PRICE]), 0)

    def test_flat_and_rising_series(self):
        self.assertEqual(self.solve([3, 3, 3, 3]), 0)
        self.assertEqual(self.solve([1, 2, 3, 4, 5]), 4)
        self.assertEqual(self.solve([5, 4, 3, 2, 1]), 0)
        self.assertEqual(self.solve([2, 1, 2, 0, 1]), 1)

    def test_best_trade_is_not_always_at_the_ends(self):
        # The cheapest day is not the first and the dearest is not the last.
        self.assertEqual(self.solve([3, 8, 1, 2]), 5)
        self.assertEqual(self.solve([2, 4, 1]), 2)
        self.assertEqual(self.solve([2, 4, 1]), brute_force([2, 4, 1]))

    def test_price_boundaries(self):
        self.assertEqual(self.solve([0, MAX_PRICE]), MAX_PRICE)
        self.assertEqual(self.solve([MAX_PRICE, 0]), 0)
        self.assertEqual(self.solve([0] * 10 + [MAX_PRICE]), MAX_PRICE)

    def test_exhaustive_small_series(self):
        for length in range(1, 7):
            for prices in itertools.product((0, 1, 2, 5), repeat=length):
                with self.subTest(prices=prices):
                    self.assertEqual(self.solve(list(prices)), brute_force(list(prices)))
                    self.assertEqual(self.solve(list(prices)), kadane_on_deltas(list(prices)))

    def test_random_series_against_both_oracles(self):
        rng = random.Random(1210)
        for _ in range(600):
            length = rng.randint(1, 40)
            prices = [rng.randint(0, 30) for _ in range(length)]
            with self.subTest(prices=prices):
                self.assertEqual(self.solve(prices), brute_force(prices))
                self.assertEqual(self.solve(prices), kadane_on_deltas(prices))

    def test_constraint_sized(self):
        rng = random.Random(1211)
        prices = [rng.randint(0, MAX_PRICE) for _ in range(MAX_DAYS)]
        self.assertEqual(self.solve(prices), kadane_on_deltas(prices))

        # A deep valley in the middle: the buy day is not day 0 and the sell day
        # is not the last one. Padding with the peak keeps the answer at the
        # valley-to-peak climb.
        valley = [MAX_PRICE] * (MAX_DAYS - 30002)
        valley += [0] * 10000
        valley += list(range(MAX_PRICE + 1))
        valley += list(range(MAX_PRICE, -1, -1))
        self.assertEqual(len(valley), MAX_DAYS)
        self.assertEqual(self.solve(valley), MAX_PRICE)
        self.assertEqual(self.solve(valley), kadane_on_deltas(valley))

        # Monotone series at the constraint size, all inside [0, 10^4].
        rising = list(range(MAX_PRICE + 1)) + [MAX_PRICE] * (MAX_DAYS - MAX_PRICE - 1)
        self.assertEqual(len(rising), MAX_DAYS)
        self.assertEqual(self.solve(rising), MAX_PRICE)

        falling = list(range(MAX_PRICE, -1, -1)) + [0] * (MAX_DAYS - MAX_PRICE - 1)
        self.assertEqual(len(falling), MAX_DAYS)
        self.assertEqual(self.solve(falling), 0)

        self.assertEqual(self.solve([MAX_PRICE] * MAX_DAYS), 0)
        self.assertEqual(self.solve([0] * (MAX_DAYS - 1) + [MAX_PRICE]), MAX_PRICE)


if __name__ == '__main__':
    unittest.main()
