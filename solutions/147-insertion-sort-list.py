# 147. Insertion Sort List
# https://leetcode.com/problems/insertion-sort-list/
#
# Literal insertion sort on the list, relinking the existing nodes: a dummy
# head starts the sorted part, and each node is detached from the input and
# spliced after the last sorted node whose value is <= its own (`<=` keeps the
# sort stable for equal values).
#
# Invariant: at the top of the loop, dummy.next heads a sorted run of exactly
# the nodes already consumed, and `tail` is its last node. `following` is saved
# before the current node is relinked, so the untouched remainder stays
# reachable. The fast path appends when the new value is at least the tail's,
# which is what makes already-sorted input linear.
#
# Time: O(n^2) worst case, O(n) on sorted input   Space: O(1) extra

class Solution:
    def insertionSortList(self, head: "ListNode | None") -> "ListNode | None":
        dummy = ListNode(0)
        tail = None
        current = head
        while current is not None:
            following = current.next
            if tail is not None and tail.val <= current.val:
                # Fast path: it belongs at the end of the sorted run.
                tail.next = current
                tail = current
            else:
                previous = dummy
                while previous.next is not None and previous.next.val <= current.val:
                    previous = previous.next
                current.next = previous.next
                previous.next = current
                if current.next is None:
                    tail = current
            current = following
        if tail is not None:
            tail.next = None
        return dummy.next
