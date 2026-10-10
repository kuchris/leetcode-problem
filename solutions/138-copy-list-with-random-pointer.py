# 138. Copy List with Random Pointer
# https://leetcode.com/problems/copy-list-with-random-pointer/
#
# Two passes with a dictionary keyed by the original node object:
#
#   - First pass walks `next` and creates one fresh Node per original, storing
#     `clones[original]`. Keying by identity (Node defines no __eq__) is what
#     makes the mapping one-to-one even when values repeat.
#   - Second pass walks `next` again and wires each copy's `next` and `random` to
#     `clones[...]` of the corresponding original, skipping the pointers that are
#     None.
#
# Invariant: after the first pass every original has exactly one clone and no
# clone has any pointer set; after the second pass every pointer of a clone that
# is not None is a clone, never an original node, and it mirrors the original's
# pointer. The original list is never written to.
#
# Time: O(n)   Space: O(n)   (n = list length; the dictionary and the copies)

class Solution:
    def copyRandomList(self, head: "Node | None") -> "Node | None":
        if head is None:
            return None

        clones: dict = {}
        node = head
        while node is not None:
            clones[node] = Node(node.val)
            node = node.next

        node = head
        while node is not None:
            clone = clones[node]
            if node.next is not None:
                clone.next = clones[node.next]
            if node.random is not None:
                clone.random = clones[node.random]
            node = node.next

        return clones[head]
