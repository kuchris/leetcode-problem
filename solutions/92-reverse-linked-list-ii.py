# 92. Reverse Linked List II
# https://leetcode.com/problems/reverse-linked-list-ii/
#
# One pass with a dummy node in front of the head, so left == 1 needs no special
# case. Walk `before` to the node just in front of position `left` (left - 1
# steps from the dummy).
#
# Invariant: `before.next .. tail` is the already reversed portion of the
# segment (initially just the node at position `left`, which is also its tail),
# and the loop repeats right - left times, each time taking the first node of the
# not-yet-reversed remainder (`tail.next`), unlinking it, and splicing it
# directly after `before`, i.e. at the front of the reversed block. After
# right - left moves the whole segment is reversed, and `tail` still points at
# the segment's last node, which already links to the untouched suffix.
#
# Time: O(n)   Space: O(1)   (n = number of nodes)

class Solution:
    def reverseBetween(self, head: "ListNode | None", left: int, right: int) -> "ListNode | None":
        dummy = ListNode(0, head)
        before = dummy
        for _ in range(left - 1):
            before = before.next

        tail = before.next  # node at position `left`; becomes the segment's tail
        for _ in range(right - left):
            node = tail.next        # first node still in original order
            tail.next = node.next   # unlink it
            node.next = before.next  # splice it at the front of the block
            before.next = node

        return dummy.next
