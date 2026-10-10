# 122. Best Time to Buy and Sell Stock II
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/
#
# Unlimited transactions (one share held at a time). Any rising run can be
# harvested edge by edge: buying at i and selling at i + 1 for every step of a
# climb telescopes to the same total as holding through it, and skipping an edge
# whose price falls avoids a loss. Conversely every unit of profit is a sum of
# consecutive day-to-day differences, so no strategy beats adding up the
# positive ones.
#
# Invariant: after processing the pair (prices[i], prices[i+1]), the accumulator
# equals the best profit obtainable from the first i + 1 days. Selling and
# re-buying on the same day is allowed by the statement, so no other restriction
# binds.
#
# Time: O(n)   Space: O(1)

class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        profit = 0
        for today, tomorrow in zip(prices, prices[1:]):
            if tomorrow > today:
                profit += tomorrow - today
        return profit
