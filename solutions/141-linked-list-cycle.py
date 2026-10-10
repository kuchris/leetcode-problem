# 141. Linked List Cycle
# https://leetcode.com/problems/linked-list-cycle/
#
# Floyd's tortoise and hare: walk one pointer one step at a time and the other
# two steps at a time. If the list is acyclic the fast pointer reaches the end;
# if it has a cycle the two must meet, because inside the cycle the fast pointer
# closes the gap to the slow one by exactly one node per step, so the gap (which
# is finite and taken modulo the cycle length) eventually becomes zero.
#
# Invariant: before each iteration both pointers are inside the list, so
# `fast is not None and fast.next is not None` is exactly the condition for the
# two-step move to stay inside; the loop returns True only when the pointers are
# the same object, which can only happen if that node was revisited.
#
# Only two pointers are used, so the extra space is O(1) (the intended follow-up),
# and the list is never modified.
#
# Time: O(n)   Space: O(1)

class Solution:
    def hasCycle(self, head: "ListNode | None") -> bool:
        slow = head
        fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False
