# 173. Binary Search Tree Iterator
# https://leetcode.com/problems/binary-search-tree-iterator/
#
# Entry point: BSTIterator
# LeetCode judges this problem through BSTIterator, not Solution -- the template
# defines no Solution class, so a Solution here would never be instantiated.
#
# The iterator keeps the left spine of the nodes still to visit: the path from
# the current position down to the next node in inorder, with that next node on
# top of the stack. next() pops the top node (the smallest unvisited key, because
# everything left of it was already emitted) and then pushes the left spine of
# that node's right child, which is precisely the next run of keys in inorder.
#
# Invariant: the stack holds the unvisited ancestors whose left subtrees are
# exhausted, ordered so the top is the smallest unvisited key. Pushing a left
# spine preserves that order, and pushing nothing for a missing child correctly
# leaves the following ancestor on top. hasNext() is therefore just "the stack is
# non-empty", and it is exact because the stack is empty only after the largest
# key has been popped.
#
# Each node is pushed and popped exactly once over the whole iteration, so both
# methods are O(1) amortised, and the stack never grows beyond one root-to-leaf
# path: O(h) memory, which is the stated follow-up.
#
# Time: O(1) amortised per next()/hasNext()   Space: O(h) for the stack

class BSTIterator:
    def __init__(self, root: "TreeNode | None"):
        self.stack: "list[TreeNode]" = []
        self.push_left_spine(root)

    def push_left_spine(self, node: "TreeNode | None") -> None:
        while node is not None:
            self.stack.append(node)
            node = node.left

    def next(self) -> int:
        node = self.stack.pop()
        self.push_left_spine(node.right)
        return node.val

    def hasNext(self) -> bool:
        return bool(self.stack)
