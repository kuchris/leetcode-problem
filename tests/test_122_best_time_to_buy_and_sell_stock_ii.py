"""Tests for 122. Best Time to Buy and Sell Stock II.

Oracles:
  - ``brute_force``: a recursive enumeration of every legal action sequence
    (do nothing / buy / sell), exponential, so used for short series only.
  - ``state_dp``: a holding/not-holding state machine over the days, a
    formulation deliberately different from the solution's sum of positive
    day-to-day rises.
  - closed forms: a non-increasing series is worth 0 and a series that only
    rises is worth last - first, whatever the transaction count.

Exhaustive sweep: every series of length 1..5 over {0, 1, 3, 5} against the
brute force, and the same lengths over {0, 3} up to length 7, plus all of them
against the state DP.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('122-best-time-to-buy-and-sell-stock-ii.py').Solution

MAX_DAYS = 3 * 10 ** 4
MAX_PRICE = 10 ** 4


def brute_force(prices) -> int:
    """Every action sequence; at most one action per day loses nothing."""
    best = 0

    def walk(day, holding, cash):
        nonlocal best
        if day == len(prices):
            best = max(best, cash)
            return
        price = prices[day]
        walk(day + 1, holding, cash)              # do nothing
        if holding:
            walk(day + 1, False, cash + price)    # sell
        else:
            walk(day + 1, True, cash - price)     # buy

    walk(0, False, 0)
    return best


def state_dp(prices) -> int:
    """cash / hold balances after each day, updated simultaneously."""
    cash = 0
    hold = -prices[0]
    for price in prices[1:]:
        cash, hold = max(cash, hold + price), max(hold, cash - price)
    return cash


class BestTimeToBuyAndSellStockIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maxProfit

    def test_official_examples(self):
        self.assertEqual(self.solve([7, 1, 5, 3, 6, 4]), 7)
        self.assertEqual(self.solve([1, 2, 3, 4, 5]), 4)
        self.assertEqual(self.solve([7, 6, 4, 3, 1]), 0)

    def test_single_day_cannot_trade(self):
        self.assertEqual(self.solve([0]), 0)
        self.assertEqual(self.solve([MAX_PRICE]), 0)

    def test_more_transactions_than_one_rise(self):
        # Two separate climbs beat holding through the dip.
        self.assertEqual(self.solve([1, 5, 1, 5]), 8)
        self.assertEqual(self.solve([1, 5, 1, 5]), brute_force([1, 5, 1, 5]))
        self.assertEqual(self.solve([3, 2, 6, 5, 0, 3]), 7)
        self.assertEqual(self.solve([3, 2, 6, 5, 0, 3]), state_dp([3, 2, 6, 5, 0, 3]))

    def test_sawtooth_alternates_every_day(self):
        self.assertEqual(self.solve([1, 2, 1, 2, 1, 2, 1, 2]), 4)
        self.assertEqual(self.solve([0, MAX_PRICE, 0, MAX_PRICE]), 2 * MAX_PRICE)

    def test_exhaustive_small_series(self):
        for length in range(1, 6):
            for prices in itertools.product((0, 1, 3, 5), repeat=length):
                prices = list(prices)
                with self.subTest(prices=prices):
                    self.assertEqual(self.solve(prices), brute_force(prices))
                    self.assertEqual(self.solve(prices), state_dp(prices))
        for length in range(6, 8):
            for prices in itertools.product((0, 3), repeat=length):
                prices = list(prices)
                with self.subTest(prices=prices):
                    self.assertEqual(self.solve(prices), brute_force(prices))
                    self.assertEqual(self.solve(prices), state_dp(prices))

    def test_random_series_against_both_oracles(self):
        rng = random.Random(1220)
        for _ in range(400):
            length = rng.randint(1, 9)
            prices = [rng.randint(0, 12) for _ in range(length)]
            with self.subTest(prices=prices):
                self.assertEqual(self.solve(prices), brute_force(prices))
                self.assertEqual(self.solve(prices), state_dp(prices))

    def test_constraint_sized(self):
        rng = random.Random(1221)
        prices = [rng.randint(0, MAX_PRICE) for _ in range(MAX_DAYS)]
        self.assertEqual(self.solve(prices), state_dp(prices))

        # A series that never rises can never be traded profitably.
        falling = list(range(MAX_PRICE, -1, -1)) + [0] * (MAX_DAYS - MAX_PRICE - 1)
        self.assertEqual(len(falling), MAX_DAYS)
        self.assertEqual(self.solve(falling), 0)

        # A staircase cycling through every price: checked against the DP.
        rising = []
        value = 0
        while len(rising) < MAX_DAYS:
            rising.append(value)
            value = (value + 1) % (MAX_PRICE + 1)
        self.assertEqual(self.solve(rising), state_dp(rising))

        # One climb from the floor to the ceiling: exactly one rise to harvest.
        step = [0] * (MAX_DAYS // 2) + [MAX_PRICE] * (MAX_DAYS - MAX_DAYS // 2)
        self.assertEqual(len(step), MAX_DAYS)
        self.assertEqual(self.solve(step), MAX_PRICE)
        self.assertEqual(self.solve(step), state_dp(step))

        # The floor and the ceiling alternating every day.
        alternating = [0, MAX_PRICE] * (MAX_DAYS // 2)
        self.assertEqual(len(alternating), MAX_DAYS)
        self.assertEqual(self.solve(alternating), (MAX_DAYS // 2) * MAX_PRICE)

        self.assertEqual(self.solve([MAX_PRICE] * MAX_DAYS), 0)


if __name__ == '__main__':
    unittest.main()
