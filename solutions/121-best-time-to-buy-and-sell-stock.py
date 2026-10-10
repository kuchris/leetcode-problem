# 121. Best Time to Buy and Sell Stock
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
#
# One transaction: pick a buy day i and a later sell day j > i, maximise
# prices[j] - prices[i]. Scanning left to right, the best sell on day j uses the
# cheapest price seen strictly before j, so a single pass suffices.
#
# Invariant: before day j is processed, `lowest` is min(prices[0..j-1]) and
# `best` is the best profit achievable with both days inside prices[0..j-1].
# The buy day is always earlier because `lowest` is only updated after the
# profit for day j has been considered.
#
# Time: O(n)   Space: O(1)

class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        lowest = prices[0]
        best = 0
        for price in prices[1:]:
            best = max(best, price - lowest)
            lowest = min(lowest, price)
        return best
