# 188. Best Time to Buy and Sell Stock IV
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/
#
# State machine over transactions: `hold[t]` is the best cash balance after
# buying for the t-th time and `cash[t]` after selling for the t-th time, with
# cash[0] = 0 (nothing done) and hold[0] unreachable.
#
# Each day, for t from k down to 1, either start/extend the t-th purchase with
# `cash[t - 1] - price` or close it with `hold[t] + price`. The descending loop
# is what makes it correct: `cash[t - 1]` is still yesterday's value when
# `hold[t]` is updated, so a sale cannot fund a new purchase on the same day,
# while buying and selling the same t on one day is a no-op that can never
# inflate the answer.
#
# At most floor(n / 2) transactions can ever be used (each needs two distinct
# days and they never overlap), so capping k there implements the "k >= n / 2 is
# unlimited trading" case exactly while bounding the work.
#
# Time: O(n * min(k, n / 2))   Space: O(min(k, n / 2))

class Solution:
    def maxProfit(self, k: int, prices: list[int]) -> int:
        if k <= 0 or len(prices) < 2:
            return 0
        limit = min(k, len(prices) // 2)
        hold = [-10 ** 18] * (limit + 1)
        cash = [0] * (limit + 1)
        for price in prices:
            for t in range(limit, 0, -1):
                hold[t] = max(hold[t], cash[t - 1] - price)
                cash[t] = max(cash[t], hold[t] + price)
        return cash[limit]
