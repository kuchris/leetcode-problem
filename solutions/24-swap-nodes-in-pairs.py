# 24. Swap Nodes in Pairs
# https://leetcode.com/problems/swap-nodes-in-pairs/
#
# Relink the nodes instead of swapping values. A dummy head makes the first
# pair no different from the rest: for each pair, point the previous node at
# the second node, let the second node point at the first, and let the first
# node inherit the remainder. The loop stops when fewer than two nodes remain,
# which leaves an odd tail untouched.
#
# The ListNode annotations are quoted so they stay unevaluated strings, keeping
# the file loadable outside the judge without a __future__ import.
#
# Time: O(n)   Space: O(1)


class Solution:
    def swapPairs(self, head: "ListNode | None") -> "ListNode | None":
        dummy = ListNode(0, head)
        previous = dummy

        while previous.next is not None and previous.next.next is not None:
            first = previous.next
            second = first.next

            first.next = second.next
            second.next = first
            previous.next = second

            # `first` is now the tail of the swapped pair.
            previous = first

        return dummy.next
