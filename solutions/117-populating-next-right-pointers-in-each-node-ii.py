# 117. Populating Next Right Pointers in Each Node II
# https://leetcode.com/problems/populating-next-right-pointers-in-each-node-ii/
#
# The tree is not necessarily perfect, so the next neighbour of a node can sit
# several branches away. Walk one level at a time and build the level below
# while walking the current one: `previous` is the last child seen on the level
# below and `next_start` is its first child. Because the current level is
# traversed left to right through the `next` links that were set one iteration
# earlier, the children are appended to the lower level in exactly left-to-right
# order, which is precisely the order the lower level's `next` links need.
#
# Invariant: when the inner loop starts at `level_start`, every node of that
# level is reachable by following `next`, and after the loop `next_start` is the
# leftmost node of the next non-empty level, or None if the level is the last.
# Each node is visited once as a parent and once as a child, so no queue or
# recursion is needed: O(1) extra space.
#
# Time: O(n)   Space: O(1)

class Solution:
    def connect(self, root: 'Node') -> 'Node':
        level_start = root
        while level_start is not None:
            current = level_start
            next_start = None
            previous = None
            while current is not None:
                for child in (current.left, current.right):
                    if child is None:
                        continue
                    if previous is None:
                        next_start = child
                    else:
                        previous.next = child
                    previous = child
                current = current.next
            level_start = next_start
        return root
