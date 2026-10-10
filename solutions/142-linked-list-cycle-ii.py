# 142. Linked List Cycle II
# https://leetcode.com/problems/linked-list-cycle-ii/
#
# First find a meeting point with Floyd's tortoise and hare (problem 141). Let
# the tail before the cycle have length a, the cycle have length c, and the
# meeting point sit b steps into the cycle. When they meet, the slow pointer has
# walked a + b and the fast one a + b + k*c for some k, and the fast pointer
# walked exactly twice as far, so a + b = k*c, i.e. a = k*c - b. That is the
# distance from the meeting point forward to the cycle entry.
#
# Invariant of the second loop: `entry` starts at the head and `slow` at the
# meeting point; both advance one step, and because the lengths above are equal
# modulo the cycle they meet exactly at the first node of the cycle. Advancing
# only one step at a time and comparing identity makes the returned node the
# actual entry object.
#
# Only two extra pointers are used (O(1) space), and the list is not modified.
#
# Time: O(n)   Space: O(1)

class Solution:
    def detectCycle(self, head: "ListNode | None") -> "ListNode | None":
        slow = head
        fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                entry = head
                while entry is not slow:
                    entry = entry.next
                    slow = slow.next
                return entry
        return None
