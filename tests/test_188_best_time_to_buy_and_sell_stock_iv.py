"""Tests for 188. Best Time to Buy and Sell Stock IV.

Oracles:
  - ``brute_force``: recursively explores do-nothing / buy / sell on every day
    with an explicit transaction counter — the definition, with no DP at all.
    Exponential, so it is used for n <= 9.
  - ``day_table_dp``: an independent DP with a different state definition — a
    cash/hold table per completed-sale count, rebuilt from *copies* of the
    previous day (no in-place update, no k capping, no descending loop). It is
    the oracle for the 1000-day cases.
  - closed forms: k = 0 is worth nothing; a series that never falls is worth
    last - first whatever k is; and k >= n // 2 must equal unlimited trading
    (the sum of the positive daily rises), which is the degenerate case the
    statement implies but does not spell out.

Exhaustive sweep: every price series of length 1..5 over {0, 1, 3, 5} for
k in {0, 1, 2, 3}, and every length-6 series over {0, 3} for k in {0, 1, 2, 3, 6}.
"""

import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('188-best-time-to-buy-and-sell-stock-iv.py').Solution

MAX_DAYS = 1000
MAX_K = 100
MAX_PRICE = 1000
UNREACHABLE = -10 ** 18


def brute_force(k, prices) -> int:
    """Every legal action sequence, with an explicit count of completed buys."""
    best = 0

    def walk(day, holding, profit, used):
        nonlocal best
        if not holding:
            best = max(best, profit)
        if day == len(prices):
            return
        walk(day + 1, holding, profit, used)                    # do nothing
        if holding:
            walk(day + 1, False, profit + prices[day], used)    # sell
        elif used < k:
            walk(day + 1, True, profit - prices[day], used + 1)  # buy

    walk(0, False, 0, 0)
    return best


def day_table_dp(k, prices) -> int:
    """cash[t] after t completed sales and hold[t] while holding, per day copies.

    A buy from cash[t] leaves the count at t (the purchase only *starts* the
    (t + 1)-th transaction), and a sale from hold[t] completes it, producing
    cash[t + 1]. Buys are only allowed while t < k.
    """
    if k <= 0 or len(prices) < 2:
        return 0
    cash = [0] + [UNREACHABLE] * k
    hold = [UNREACHABLE] * (k + 1)
    for price in prices:
        next_cash = list(cash)
        next_hold = list(hold)
        for t in range(k + 1):
            if hold[t] != UNREACHABLE and t + 1 <= k:
                next_cash[t + 1] = max(next_cash[t + 1], hold[t] + price)
            if cash[t] != UNREACHABLE and t < k:
                next_hold[t] = max(next_hold[t], cash[t] - price)
        cash, hold = next_cash, next_hold
    return max(cash)


def unlimited(prices) -> int:
    """Unlimited transactions: every positive daily rise is harvestable."""
    return sum(max(0, later - earlier) for earlier, later in zip(prices, prices[1:]))


class BestTimeToBuyAndSellStockIVTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().maxProfit

    def check(self, k, prices):
        result = self.solve(k, list(prices))
        self.assertEqual(result, brute_force(k, prices))
        self.assertEqual(result, day_table_dp(k, prices))
        return result

    def test_official_examples(self):
        self.assertEqual(self.solve(2, [2, 4, 1]), 2)
        self.assertEqual(self.solve(2, [3, 2, 6, 5, 0, 3]), 7)
        self.check(2, [2, 4, 1])
        self.check(2, [3, 2, 6, 5, 0, 3])

    def test_zero_transactions_or_one_day(self):
        self.assertEqual(self.solve(0, [2, 4, 1]), 0)
        self.assertEqual(self.solve(0, [1, 2, 3, 4, 5]), 0)
        self.assertEqual(self.solve(0, [5, 4, 3, 2, 1]), 0)
        for prices in ([0], [7], [MAX_PRICE]):
            with self.subTest(prices=prices):
                self.assertEqual(self.solve(1, prices), 0)
                self.assertEqual(self.solve(100, prices), 0)

    def test_one_transaction_matches_the_single_trade_answer(self):
        rng = random.Random(1880)
        for _ in range(300):
            length = rng.randint(1, 12)
            prices = [rng.randint(0, 20) for _ in range(length)]
            expected = max(
                (prices[j] - prices[i]
                 for i in range(length) for j in range(i + 1, length)),
                default=0,
            )
            with self.subTest(prices=prices):
                self.assertEqual(self.solve(1, prices), max(0, expected))

    def test_more_transactions_than_rises_is_pointless(self):
        self.assertEqual(self.solve(2, [1, 5, 1, 5]), 8)
        self.assertEqual(self.solve(3, [1, 5, 1, 5]), 8)
        self.assertEqual(self.solve(100, [1, 5, 1, 5]), 8)
        self.assertEqual(self.solve(1, [1, 5, 1, 5]), 4)

    def test_k_at_least_half_the_days_is_unlimited_trading(self):
        rng = random.Random(1881)
        for _ in range(60):
            length = rng.randint(2, 30)
            prices = [rng.randint(0, 25) for _ in range(length)]
            big = length // 2
            with self.subTest(prices=prices):
                self.assertEqual(self.solve(big, prices), unlimited(prices))
                self.assertEqual(self.solve(big, prices), day_table_dp(big, prices))
                self.assertEqual(self.solve(length, prices), unlimited(prices))
                self.assertLessEqual(self.solve(big - 1, prices), unlimited(prices))

    def test_exhaustive_short_series(self):
        for length in range(1, 6):
            for prices in itertools.product((0, 1, 3, 5), repeat=length):
                prices = list(prices)
                for k in (0, 1, 2, 3):
                    with self.subTest(prices=prices, k=k):
                        self.check(k, prices)
        for prices in itertools.product((0, 3), repeat=6):
            prices = list(prices)
            for k in (0, 1, 2, 3, 6):
                with self.subTest(prices=prices, k=k):
                    self.check(k, prices)

    def test_random_series_and_k(self):
        rng = random.Random(1882)
        for _ in range(400):
            length = rng.randint(1, 9)
            prices = [rng.randint(0, 12) for _ in range(length)]
            k = rng.randint(0, 6)
            with self.subTest(prices=prices, k=k):
                self.check(k, prices)

    def test_input_is_not_mutated(self):
        prices = [3, 2, 6, 5, 0, 3]
        copy = list(prices)
        self.solve(2, prices)
        self.assertEqual(prices, copy)

    def test_constraint_sized(self):
        rng = random.Random(1883)
        prices = [rng.randint(0, MAX_PRICE) for _ in range(MAX_DAYS)]
        self.assertEqual(self.solve(MAX_K, prices), day_table_dp(MAX_K, prices))

        # The degenerate cases the statement implies.
        rising = list(range(MAX_DAYS))
        self.assertEqual(self.solve(1, rising), MAX_DAYS - 1)
        self.assertEqual(self.solve(MAX_K, rising), MAX_DAYS - 1)
        self.assertEqual(self.solve(MAX_DAYS // 2, rising), MAX_DAYS - 1)
        falling = list(range(MAX_DAYS, 0, -1))
        self.assertEqual(self.solve(MAX_K, falling), 0)
        self.assertEqual(self.solve(MAX_DAYS, [MAX_PRICE] * MAX_DAYS), 0)

        # Many small rises: k >= n // 2 must harvest every one of them.
        sawtooth = [0, MAX_PRICE] * (MAX_DAYS // 2)
        self.assertEqual(len(sawtooth), MAX_DAYS)
        expected = (MAX_DAYS // 2) * MAX_PRICE
        self.assertEqual(self.solve(MAX_DAYS // 2, sawtooth), expected)
        self.assertEqual(self.solve(MAX_K, sawtooth), day_table_dp(MAX_K, sawtooth))
        self.assertEqual(self.solve(MAX_DAYS, sawtooth), expected)

        # k just below the unlimited threshold can still be enough here.
        self.assertEqual(self.solve(1, sawtooth), MAX_PRICE)


if __name__ == '__main__':
    unittest.main()
