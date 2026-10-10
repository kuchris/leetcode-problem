# 86. Partition List
# https://leetcode.com/problems/partition-list/
#
# Two dummy-headed chains, one for values < x and one for values >= x. A single
# pass moves every node to the tail of its chain, and each node is detached from
# its old successor before being re-linked, so no stale pointer can survive into
# the result (a node's original next may belong to the other partition).
#
# Invariant: after each step the two chains contain exactly the nodes seen so
# far, in their original relative order, split by the comparison with x. The
# final join puts the >= chain after the < chain, which also handles an empty
# side because both dummies start with next = None.
#
# Time: O(n)   Space: O(1)   (n = number of nodes; only two dummy nodes are added)

class Solution:
    def partition(self, head: "ListNode | None", x: int) -> "ListNode | None":
        less_dummy = ListNode(0)
        less_tail = less_dummy
        greater_dummy = ListNode(0)
        greater_tail = greater_dummy

        node = head
        while node is not None:
            following = node.next
            node.next = None  # detach before re-linking
            if node.val < x:
                less_tail.next = node
                less_tail = node
            else:
                greater_tail.next = node
                greater_tail = node
            node = following

        less_tail.next = greater_dummy.next
        return less_dummy.next
