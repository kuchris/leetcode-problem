# 61. Rotate List
# https://leetcode.com/problems/rotate-list/
#
# Rotating right by k places is the same as cutting the list after position
# length - k and moving the tail to the front. Three facts make it one pass plus
# one walk:
#
#   - k can exceed the length, and rotating by the length changes nothing, so
#     only k % length matters;
#   - the last node is needed anyway to close the ring, and walking to it also
#     measures the length;
#   - once the ring is closed, the new head is the node after the new tail, and
#     breaking the link there yields the rotated list.
#
# The ListNode annotations are quoted so they stay unevaluated strings, keeping
# the file loadable outside the judge without a future-annotations import.
#
# Time: O(n)   Space: O(1)

class Solution:
    def rotateRight(self, head: "ListNode | None", k: int) -> "ListNode | None":
        if head is None or head.next is None or k == 0:
            return head

        length = 1
        tail = head
        while tail.next is not None:
            tail = tail.next
            length += 1

        k %= length
        if k == 0:
            return head

        # The new tail sits length - k - 1 steps from the head.
        new_tail = head
        for _ in range(length - k - 1):
            new_tail = new_tail.next

        new_head = new_tail.next
        new_tail.next = None
        tail.next = head
        return new_head
