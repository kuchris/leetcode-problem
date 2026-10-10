# 133. Clone Graph
# https://leetcode.com/problems/clone-graph/
#
# One traversal with a dictionary keyed by the original node object:
#
#   - `clones[original]` is that node's copy. It is created the first time the
#     original is seen, which is what guarantees exactly one copy per node even
#     when the graph has cycles.
#   - The stack holds originals whose copies exist but whose neighbour lists are
#     not finished. Popping one appends `clones[neighbor]` for every neighbour,
#     creating that copy first if needed, so every edge is written exactly once.
#
# Invariant: for every original node popped so far, its copy's neighbour list is
# complete and holds only copies. Because keys are the original objects (identity
# hashing, as Node defines no __eq__), no copy can ever be reached from the
# original graph and no original leaks into the copy.
#
# Time: O(V + E)   Space: O(V)

class Solution:
    def cloneGraph(self, node: "Node | None") -> "Node | None":
        if node is None:
            return None

        clones = {node: Node(node.val)}
        stack = [node]

        while stack:
            current = stack.pop()
            for neighbor in current.neighbors:
                if neighbor not in clones:
                    clones[neighbor] = Node(neighbor.val)
                    stack.append(neighbor)
                clones[current].neighbors.append(clones[neighbor])

        return clones[node]
