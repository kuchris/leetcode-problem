# 129. Sum Root to Leaf Numbers
# https://leetcode.com/problems/sum-root-to-leaf-numbers/
#
# Pre-order DFS carrying the number spelled by the path from the root. Entering a
# node of value v replaces the carried value `acc` with `acc * 10 + v`, which is
# exactly "append the digit v". A node with no children ends a root-to-leaf
# number, so its carried value is added to the total; internal nodes just pass
# their value down to both children.
#
# Invariant: the value pushed with a child is the number spelled by the
# root-to-that-child path. The walk is iterative so that a deep tree cannot
# exhaust the interpreter stack; the depth is bounded by the problem's depth
# limit either way.
#
# Time: O(n)   Space: O(n)   (n = number of nodes; the stack holds at most one
# entry per node on the current frontier)

class Solution:
    def sumNumbers(self, root: "TreeNode | None") -> int:
        total = 0
        stack = [(root, 0)]

        while stack:
            node, acc = stack.pop()
            acc = acc * 10 + node.val

            if node.left is None and node.right is None:
                total += acc
                continue
            if node.left is not None:
                stack.append((node.left, acc))
            if node.right is not None:
                stack.append((node.right, acc))

        return total
