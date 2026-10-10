"""Tests for 123. Best Time to Buy and Sell Stock III.

Oracles:
  - ``brute_force``: every pair of disjoint (buy, sell) intervals, plus the
    single-transaction and no-transaction plans — the definition of "at most
    two transactions", no state machine involved.
  - ``split_oracle``: for each split point, the best single trade strictly
    before it plus the best single trade from it onwards (prefix/suffix scans).
    A genuinely different decomposition from the solution's four balances, and
    the one used for the 10^5-day cases.
  - closed forms: a non-increasing series is worth 0; a series that only rises
    is worth last - first, because splitting a climb adds nothing.

Exhaustive sweep: every series of length 1..5 over {0, 1, 3, 5} against both
oracles, and lengths 6..7 over {0, 3}.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('123-best-time-to-buy-and-sell-stock-iii.py').Solution

MAX_DAYS = 10 ** 5
MAX_PRICE = 10 ** 5


def brute_force(prices) -> int:
    """Best profit from at most two non-overlapping bought-then-sold trades."""
    size = len(prices)
    best = 0
    for buy in range(size):
        for sell in range(buy + 1, size):
            best = max(best, prices[sell] - prices[buy])
    for buy1 in range(size):
        for sell1 in range(buy1 + 1, size):
            first = prices[sell1] - prices[buy1]
            for buy2 in range(sell1 + 1, size):
                for sell2 in range(buy2 + 1, size):
                    best = max(best, first + prices[sell2] - prices[buy2])
    return best


def split_oracle(prices) -> int:
    """Best one-trade profit on each prefix plus best one-trade on each suffix."""
    size = len(prices)
    prefix = [0] * (size + 1)
    lowest = prices[0]
    for end in range(1, size + 1):
        lowest = min(lowest, prices[end - 1])
        prefix[end] = max(prefix[end - 1], prices[end - 1] - lowest)

    suffix = [0] * (size + 1)
    highest = prices[-1]
    for start in range(size - 1, -1, -1):
        highest = max(highest, prices[start])
        suffix[start] = max(suffix[start + 1], highest - prices[start])

    return max(prefix[split] + suffix[split] for split in range(size + 1))


class BestTimeToBuyAndSellStockIIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maxProfit

    def test_official_examples(self):
        self.assertEqual(self.solve([3, 3, 5, 0, 0, 3, 1, 4]), 6)
        self.assertEqual(self.solve([1, 2, 3, 4, 5]), 4)
        self.assertEqual(self.solve([7, 6, 4, 3, 1]), 0)

    def test_single_day_cannot_trade(self):
        self.assertEqual(self.solve([0]), 0)
        self.assertEqual(self.solve([MAX_PRICE]), 0)

    def test_two_valleys_beat_one_wide_hold(self):
        # One transaction earns 6, but the two disjoint climbs earn 6 + 5.
        self.assertEqual(self.solve([1, 7, 2, 4, 7, 1]), 11)
        self.assertEqual(self.solve([1, 7, 2, 4, 7, 1]), brute_force([1, 7, 2, 4, 7, 1]))
        self.assertEqual(self.solve([3, 3, 5, 0, 0, 3, 1, 4]), 6)

    def test_both_trades_are_used_when_they_do_not_overlap(self):
        # Here two disjoint windows exist: 1 -> 5 and 3 -> 6.
        self.assertEqual(self.solve([7, 1, 5, 3, 6, 4]), 7)
        self.assertEqual(self.solve([7, 1, 5, 3, 6, 4]), brute_force([7, 1, 5, 3, 6, 4]))
        # A single rising run cannot be split into anything better.
        self.assertEqual(self.solve([1, 2, 3, 4, 5]), 4)
        self.assertEqual(self.solve([1, 2, 3, 4, 5]), split_oracle([1, 2, 3, 4, 5]))
        # The second climb is small, but it is still worth taking.
        self.assertEqual(self.solve([5, 1, 6, 2, 3]), 6)
        self.assertEqual(self.solve([5, 1, 6, 2, 3]), brute_force([5, 1, 6, 2, 3]))

    def test_flat_series(self):
        self.assertEqual(self.solve([4, 4, 4, 4]), 0)
        self.assertEqual(self.solve([0, 0]), 0)

    def test_exhaustive_small_series(self):
        for length in range(1, 6):
            for prices in itertools.product((0, 1, 3, 5), repeat=length):
                prices = list(prices)
                with self.subTest(prices=prices):
                    self.assertEqual(self.solve(prices), brute_force(prices))
                    self.assertEqual(self.solve(prices), split_oracle(prices))
        for length in range(6, 8):
            for prices in itertools.product((0, 3), repeat=length):
                prices = list(prices)
                with self.subTest(prices=prices):
                    self.assertEqual(self.solve(prices), brute_force(prices))
                    self.assertEqual(self.solve(prices), split_oracle(prices))

    def test_random_series_against_both_oracles(self):
        rng = random.Random(1230)
        for _ in range(200):
            length = rng.randint(1, 9)
            prices = [rng.randint(0, 15) for _ in range(length)]
            with self.subTest(prices=prices):
                self.assertEqual(self.solve(prices), brute_force(prices))
                self.assertEqual(self.solve(prices), split_oracle(prices))

    def test_constraint_sized(self):
        rng = random.Random(1231)
        prices = [rng.randint(0, MAX_PRICE) for _ in range(MAX_DAYS)]
        self.assertEqual(self.solve(prices), split_oracle(prices))

        # One transaction is enough when the series never falls.
        rising = list(range(MAX_DAYS))
        self.assertEqual(len(rising), MAX_DAYS)
        self.assertEqual(self.solve(rising), MAX_DAYS - 1)
        self.assertEqual(self.solve(rising), split_oracle(rising))

        # A strictly falling series: no trade at all.
        falling = list(range(MAX_DAYS, 0, -1))
        self.assertEqual(self.solve(falling), 0)
        self.assertEqual(self.solve(falling), split_oracle(falling))

        # Two clean valleys at the constraint size: the answer is their sum.
        prices = [0] * (MAX_DAYS // 4) + [MAX_PRICE] * (MAX_DAYS // 4)
        prices += [0] * (MAX_DAYS // 4) + [MAX_PRICE] * (MAX_DAYS - 3 * (MAX_DAYS // 4))
        self.assertEqual(len(prices), MAX_DAYS)
        self.assertEqual(self.solve(prices), 2 * MAX_PRICE)
        self.assertEqual(self.solve(prices), split_oracle(prices))

        # The mirror image: rise then fall, worth a single MAX_PRICE.
        single = [0] * (MAX_DAYS // 2) + [MAX_PRICE] * (MAX_DAYS - MAX_DAYS // 2)
        self.assertEqual(self.solve(single), MAX_PRICE)
        self.assertEqual(self.solve(single), split_oracle(single))
        self.assertEqual(self.solve([MAX_PRICE] * MAX_DAYS), 0)


if __name__ == '__main__':
    unittest.main()
