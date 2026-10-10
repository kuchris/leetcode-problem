# 83. Remove Duplicates from Sorted List
# https://leetcode.com/problems/remove-duplicates-from-sorted-list/
#
# Single pass with one pointer. Because the list is sorted ascending, equal
# values are contiguous, so only the next node ever needs to be compared:
#
#   - if node.next holds the same value, it is unlinked and `node` stays put so
#     the following node is compared against the same survivor;
#   - otherwise the survivor is unique so far and `node` advances.
#
# Invariant: everything up to and including `node` is already a prefix of the
# deduplicated answer, and every value in it is unique. Each iteration either
# unlinks a node or advances `node`, so the loop terminates with the head
# unchanged (the first node always survives).
#
# Time: O(n)   Space: O(1)

class Solution:
    def deleteDuplicates(self, head: "ListNode | None") -> "ListNode | None":
        node = head
        while node is not None and node.next is not None:
            if node.next.val == node.val:
                node.next = node.next.next
            else:
                node = node.next
        return head
