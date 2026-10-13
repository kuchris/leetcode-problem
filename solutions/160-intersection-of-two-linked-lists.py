# 160. Intersection of Two Linked Lists
# https://leetcode.com/problems/intersection-of-two-linked-lists/
#
# Once the two lists meet they share every node to the end, so the intersection
# is determined by the tails: the shared suffix has some length s, and a node is
# the intersection exactly when the nodes still ahead of it are equal in number
# on both sides.
#
# That gives a two-pass, O(1)-space algorithm:
#
#   - measure m and n by walking each list once;
#   - advance the longer list's pointer by |m - n|, so both pointers now sit the
#     same distance from the (shared) end;
#   - walk both at the same speed until they are the same object.
#
# Invariant: after the alignment the two pointers are always the same distance
# from the end of their lists. Therefore they are either equal already (the
# intersection) or equal to None (no intersection: both non-shared tails are
# exhausted at the same moment). The lists are only read, never relinked, and no
# value comparison is ever made -- identity is the whole point.
#
# Time: O(m + n)   Space: O(1)

class Solution:
    def getIntersectionNode(self, headA: "ListNode", headB: "ListNode") -> "ListNode | None":
        length_a = 0
        node = headA
        while node is not None:
            length_a += 1
            node = node.next

        length_b = 0
        node = headB
        while node is not None:
            length_b += 1
            node = node.next

        longer, shorter = (headA, headB) if length_a >= length_b else (headB, headA)
        for _ in range(abs(length_a - length_b)):
            longer = longer.next

        while longer is not shorter:
            longer = longer.next
            shorter = shorter.next

        return longer
