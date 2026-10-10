# 116. Populating Next Right Pointers in Each Node
# https://leetcode.com/problems/populating-next-right-pointers-in-each-node/
#
# The tree is perfect, so the children of one level can be linked while walking
# that level through the next pointers already built -- no queue at all:
#
#   - for the current node, its two children are adjacent: left.next = right;
#   - right.next must be the leftmost child of the node's right neighbour, i.e.
#     node.next.left, and None for the last node of the level.
#
# Invariant: before the outer loop moves to node.left, every next pointer inside
# node's level is already correct, so `current = current.next` walks that level
# left to right. The outer loop descends one level at a time via node = node.left
# (the leftmost node of the next level), so each level is linked exactly once
# from the level above, using O(1) extra space.
#
# Time: O(n)   Space: O(1) beyond the tree itself

class Solution:
    def connect(self, root: "Node | None") -> "Node | None":
        node = root
        while node is not None and node.left is not None:
            current = node
            while current is not None:
                current.left.next = current.right
                if current.next is not None:
                    current.right.next = current.next.left
                else:
                    current.right.next = None
                current = current.next
            node = node.left
        return root
