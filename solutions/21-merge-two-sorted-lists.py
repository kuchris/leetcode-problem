# 21. Merge Two Sorted Lists
# https://leetcode.com/problems/merge-two-sorted-lists/
#
# Standard two-pointer merge, but splicing the existing nodes instead of
# copying values. A dummy head removes the special case for choosing the first
# node; once either list runs out, the remainder of the other list is already
# sorted and can be attached in one step.
#
# The ListNode annotations are quoted so they stay unevaluated strings. That
# keeps the file loadable outside the judge (where ListNode is undefined) while
# the judge, which defines ListNode in its preamble, sees the usual signature.
# A future-annotations import would be equivalent but is rejected: the judge
# prepends its preamble, so the import is no longer the first statement.
#
# Time: O(m + n)   Space: O(1) extra (nodes are relinked, not copied)


class Solution:
    def mergeTwoLists(
        self, list1: "ListNode | None", list2: "ListNode | None"
    ) -> "ListNode | None":
        dummy = ListNode()
        tail = dummy

        while list1 is not None and list2 is not None:
            if list1.val <= list2.val:
                tail.next = list1
                list1 = list1.next
            else:
                tail.next = list2
                list2 = list2.next
            tail = tail.next

        tail.next = list1 if list1 is not None else list2
        return dummy.next
