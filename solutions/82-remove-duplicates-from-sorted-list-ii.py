# 82. Remove Duplicates from Sorted List II
# https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/
#
# A dummy node in front of the head removes the "delete the first node" special
# case. `tail` is the last node already known to survive, so the interesting
# node is always tail.next:
#
#   - if tail.next starts a run (tail.next.next has the same value), the whole
#     run is unlinked by repeatedly advancing tail.next past every node with
#     that value, and `tail` itself stays put so the new tail.next gets tested
#     too;
#   - otherwise tail.next is a value that occurs exactly once, so `tail`
#     advances onto it.
#
# Invariant: everything at or before `tail` is final and contains no duplicate
# value; each iteration either deletes at least one node or moves `tail` one
# node forward, so the loop terminates.
#
# Time: O(n)   Space: O(1)

class Solution:
    def deleteDuplicates(self, head: "ListNode | None") -> "ListNode | None":
        dummy = ListNode(0, head)
        tail = dummy

        while tail.next is not None:
            if tail.next.next is not None and tail.next.next.val == tail.next.val:
                duplicate = tail.next.val
                while tail.next is not None and tail.next.val == duplicate:
                    tail.next = tail.next.next
            else:
                tail = tail.next

        return dummy.next
