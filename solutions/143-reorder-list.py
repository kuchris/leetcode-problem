# 143. Reorder List
# https://leetcode.com/problems/reorder-list/
#
# Three O(1)-space passes over the existing nodes (no values are moved between
# nodes, and no node is created):
#
#   1. slow/fast pointers find the end of the first half (slow stops at the
#      middle node, or at the last node of the first half for even lengths);
#   2. the second half is reversed in place, starting at slow.next, so its
#      nodes are walked from the back of the list to the middle;
#   3. the two halves are merged alternately: head, last, second, second-to-last,
#      ... which is exactly L0, Ln, L1, Ln-1, ...
#
# Invariant of the merge: `first` always points at the next node of the front
# half and `reversed_half` at the next node of the back half; each iteration
# splices one back-half node directly after one front-half node and then advances
# both, so after k iterations the first 2k nodes of the answer are in place. The
# back half is never longer than the front half, so the loop stops on the last
# front-half node, which ends the list.
#
# Time: O(n)   Space: O(1)

class Solution:
    def reorderList(self, head: "ListNode | None") -> None:
        """
        Do not return anything, modify head in-place instead.
        """
        if head is None or head.next is None:
            return

        # 1) slow ends at the last node of the first half.
        slow = head
        fast = head
        while fast.next is not None and fast.next.next is not None:
            slow = slow.next
            fast = fast.next.next

        # 2) detach and reverse the second half.
        reversed_half = slow.next
        slow.next = None
        previous = None
        while reversed_half is not None:
            following = reversed_half.next
            reversed_half.next = previous
            previous = reversed_half
            reversed_half = following

        # 3) merge the reversed half into the front half, one node at a time.
        first = head
        reversed_half = previous
        while reversed_half is not None:
            first_next = first.next
            second_next = reversed_half.next
            first.next = reversed_half
            reversed_half.next = first_next
            first = first_next
            reversed_half = second_next
