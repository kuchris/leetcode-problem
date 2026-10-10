# 148. Sort List
# https://leetcode.com/problems/sort-list/
#
# Bottom-up merge sort, which meets the follow-up of O(n log n) time and O(1)
# extra space: no recursion (nothing grows with the list) and no arrays, only
# the list's own `next` pointers plus a constant number of scalars.
#
# The list is first measured, then runs of length `step` are merged pairwise by
# relinking nodes. A dummy node owns the output chain and `tail` always points
# at its last node, so the merge only ever appends an already-detached node.
#
# Invariant: before an outer pass begins, the chain from dummy.next consists of
# sorted runs of length `step`; the pass merges them into runs of length
# 2 * step, so after ceil(log2 n) passes the whole chain is one sorted run.
# Nodes are relinked, never copied or rebuilt.
#
# Time: O(n log n)   Space: O(1) extra

class Solution:
    def sortList(self, head: "ListNode | None") -> "ListNode | None":
        if head is None or head.next is None:
            return head

        size = 0
        node = head
        while node is not None:
            size += 1
            node = node.next

        dummy = ListNode(0)
        dummy.next = head
        step = 1
        while step < size:
            current = dummy.next
            tail = dummy
            while current is not None:
                left = current
                left_size = 0
                while left_size < step and current is not None:
                    current = current.next
                    left_size += 1
                right = current
                right_size = 0
                while right_size < step and current is not None:
                    current = current.next
                    right_size += 1

                while left_size > 0 or right_size > 0:
                    if right_size == 0 or (
                        left_size > 0 and right is not None and left.val <= right.val
                    ):
                        tail.next = left
                        left = left.next
                        left_size -= 1
                    else:
                        tail.next = right
                        right = right.next
                        right_size -= 1
                    tail = tail.next
                tail.next = None
            step *= 2
        return dummy.next
