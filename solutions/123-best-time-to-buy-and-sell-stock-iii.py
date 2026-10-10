# 123. Best Time to Buy and Sell Stock III
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/
#
# At most two transactions, never holding two shares at once, so a state machine
# with four balances covers every legal plan: `buy1`/`sell1` before and after the
# first sale, `buy2`/`sell2` before and after the second. Every day either does
# nothing or performs one of the four moves.
#
# Invariant after day d: buy1 is the largest cash balance (-cost of the first
# share) reachable by buying on some day <= d; sell1 the largest reachable by
# completing a first transaction; buy2 the largest reachable by then buying a
# second share; sell2 the largest reachable by completing a second transaction.
# All four start from 0 cash, so sell2 = 0 encodes "do nothing", which is the
# required answer when no profit is possible.
#
# Time: O(n)   Space: O(1)

class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        buy1 = -prices[0]
        sell1 = 0
        buy2 = -prices[0]
        sell2 = 0
        for price in prices:
            buy1 = max(buy1, -price)
            sell1 = max(sell1, buy1 + price)
            buy2 = max(buy2, sell1 - price)
            sell2 = max(sell2, buy2 + price)
        return sell2
