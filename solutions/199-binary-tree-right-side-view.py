# 199. Binary Tree Right Side View
# https://leetcode.com/problems/binary-tree-right-side-view/
#
# Level-order traversal, one level at a time. The nodes of a level are kept in
# left-to-right order, so the *last* node of the level is the one visible from the
# right, whatever shape the tree has -- including a level whose only node is a left
# child, which happens when its parent has no right child.
#
# Invariant: at the top of each iteration `level` holds every node at the current
# depth in left-to-right order. Reading level[-1] there gives the visible value,
# and appending left then right for every node builds the next level in the same
# order. The traversal is iterative, so a left-leaning tree of depth 100 cannot
# exhaust the interpreter stack.
#
# An empty tree produces an empty view, which is also what "no nodes to see"
# means; the answer always has exactly one value per level, i.e. length == height.
#
# Time: O(n)   Space: O(w)   (n = number of nodes, w = widest level; the returned
# view holds one value per level, at most h of them)

class Solution:
    def rightSideView(self, root: "TreeNode | None") -> list[int]:
        if root is None:
            return []

        view: list[int] = []
        level = [root]

        while level:
            view.append(level[-1].val)  # rightmost node of this depth
            next_level = []
            for node in level:
                if node.left is not None:
                    next_level.append(node.left)
                if node.right is not None:
                    next_level.append(node.right)
            level = next_level

        return view
