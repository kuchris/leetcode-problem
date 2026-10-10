# 25. Reverse Nodes in k-Group
# https://leetcode.com/problems/reverse-nodes-in-k-group/
#
# Work one group at a time, satisfying the O(1) memory follow-up. For each
# group: walk k nodes ahead to confirm a full group exists (otherwise the
# remainder is left alone and the answer is ready), reverse those k nodes in
# place, then splice the reversed run back between the previous group's tail
# and the untouched remainder.
#
# The ListNode annotations are quoted so they stay unevaluated strings, keeping
# the file loadable outside the judge without a __future__ import.
#
# Time: O(n)  (each node is visited a constant number of times)   Space: O(1)


class Solution:
    def reverseKGroup(self, head: "ListNode | None", k: int) -> "ListNode | None":
        dummy = ListNode(0, head)
        group_previous = dummy

        while True:
            # Confirm that k more nodes exist before touching any links.
            probe = group_previous
            counted = 0
            while probe is not None and counted < k:
                probe = probe.next
                counted += 1
            if probe is None:
                return dummy.next

            group_start = group_previous.next
            previous = None
            current = group_start
            for _ in range(k):
                following = current.next
                current.next = previous
                previous = current
                current = following

            # `previous` is the old k-th node, `current` the untouched rest.
            group_previous.next = previous
            group_start.next = current

            # `group_start` is now the tail of the reversed group.
            group_previous = group_start
