# 23. Merge k Sorted Lists
# https://leetcode.com/problems/merge-k-sorted-lists/
#
# Repeatedly take the smallest current head with a min-heap, which is the
# k-way generalisation of merging two lists. The heap holds at most one node
# per list, so each of the N nodes costs one push and one pop of O(log k).
#
# The heap entries carry the list index as a tie-breaker: without it, equal
# values would force Python to compare ListNode objects, which have no
# ordering.
#
# The ListNode annotations are quoted so they stay unevaluated strings, which
# keeps the file loadable outside the judge without a __future__ import (the
# judge prepends its preamble, so such an import would not be first).
#
# Time: O(N log k)   Space: O(k) for the heap

import heapq


class Solution:
    def mergeKLists(self, lists: "list[ListNode | None]") -> "ListNode | None":
        heap = [
            (node.val, index, node)
            for index, node in enumerate(lists)
            if node is not None
        ]
        heapq.heapify(heap)

        dummy = ListNode()
        tail = dummy

        while heap:
            _, index, node = heapq.heappop(heap)
            tail.next = node
            tail = node
            if node.next is not None:
                heapq.heappush(heap, (node.next.val, index, node.next))

        return dummy.next
