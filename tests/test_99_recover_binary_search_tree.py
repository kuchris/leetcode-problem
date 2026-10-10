"""Tests for 99. Recover Binary Search Tree.

Oracle: brute force over every pair of nodes — swap the two values, ask whether
the tree is a BST then, and swap back. With distinct keys the shape and the key
multiset admit exactly one valid filling (the k-th inorder node must hold the
k-th smallest key), so exactly one pair repairs a broken tree and that pair is
the authority the solution is checked against. The oracle never looks at
"descents", which is the reasoning the solution uses.

Broken trees are generated the way the problem guarantees them: build a valid
BST by assigning sorted keys in inorder, then exchange two of those keys.

The shape check compares node identities, so it proves the tree was repaired in
place instead of being rebuilt.
"""

import itertools
import random
import unittest

from _loader import load_solution
from _trees import TreeNode, build, from_structure, serialize

Solution = load_solution('99-recover-binary-search-tree.py').Solution


def inorder_nodes(root) -> list:
    """Inorder node list, iteratively so 1000-node chains stay testable."""
    nodes = []
    stack = []
    node = root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        nodes.append(node)
        node = node.right
    return nodes


def inorder_values(root) -> list:
    return [node.val for node in inorder_nodes(root)]


def range_check(root) -> bool:
    """Iterative (low, high) BST check; None means unbounded."""
    stack = [(root, None, None)]
    while stack:
        node, low, high = stack.pop()
        if node is None:
            continue
        if low is not None and node.val <= low:
            return False
        if high is not None and node.val >= high:
            return False
        stack.append((node.left, low, node.val))
        stack.append((node.right, node.val, high))
    return True


def identity_structure(root):
    """Flat node-identity fingerprint, pre-order: (id, id(left), id(right)).

    Comparing fingerprints proves the object graph was not rebuilt.
    """
    snapshot = []
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        snapshot.append((
            id(node),
            id(node.left) if node.left is not None else None,
            id(node.right) if node.right is not None else None,
        ))
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    return snapshot


def repairing_pairs(root) -> list:
    """Every pair of nodes whose value swap turns the tree into a valid BST."""
    nodes = inorder_nodes(root)
    values = [node.val for node in nodes]
    found = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            nodes[i].val, nodes[j].val = values[j], values[i]
            if range_check(root):
                found.append((nodes[i], nodes[j]))
            nodes[i].val, nodes[j].val = values[i], values[j]
    return found


def all_shapes(size):
    """Every binary tree shape with `size` nodes, as nested (left, right)."""
    if size == 0:
        yield None
        return
    for left_size in range(size):
        for left in all_shapes(left_size):
            for right in all_shapes(size - 1 - left_size):
                yield (left, right)


def fill_inorder(shape, values):
    """Assign `values` to a shape in inorder, which makes a valid BST."""
    iterator = iter(values)

    def ordered(node):
        if node is None:
            return None
        left, right = node
        left_structure = ordered(left)
        value = next(iterator)
        right_structure = ordered(right)
        return (value, left_structure, right_structure)

    if shape is None:
        return None
    return ordered(shape)


def build_valid_bst(size: int, rng: random.Random | None = None) -> "TreeNode | None":
    """A valid BST with the first (right-chain) shape and distinct keys."""
    if rng is None:
        numbers = list(range(size))
    else:
        numbers = sorted(rng.sample(range(-100_000, 100_000), size))
    return from_structure(fill_inorder(next(all_shapes(size)), numbers))


def balanced_from_sorted(values) -> "TreeNode | None":
    if not values:
        return None
    middle = len(values) // 2
    return TreeNode(
        values[middle],
        balanced_from_sorted(values[:middle]),
        balanced_from_sorted(values[middle + 1:]),
    )


def swap_pair(root, i, j):
    """Exchange the keys of the i-th and j-th nodes in inorder."""
    nodes = inorder_nodes(root)
    nodes[i].val, nodes[j].val = nodes[j].val, nodes[i].val
    return root


class RecoverBinarySearchTreeTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().recoverTree

    def recover(self, root):
        """Run the solution and assert the in-place contract and the result."""
        identity = identity_structure(root)
        original_values = sorted(inorder_values(root))
        self.assertIsNone(self.solve(root), 'recoverTree must modify in place')
        self.assertEqual(identity_structure(root), identity, 'the shape changed')
        self.assertEqual(inorder_values(root), original_values, 'keys not sorted')
        self.assertTrue(range_check(root))
        return root

    def test_official_examples(self):
        root = build([1, 3, None, None, 2])
        self.assertEqual(serialize(self.recover(root)), [3, 1, None, None, 2])

        root = build([3, 1, 4, None, None, 2])
        self.assertEqual(serialize(self.recover(root)), [2, 1, 4, None, None, 3])

    def test_two_nodes(self):
        # 2 must not be the left child of 1.
        root = from_structure((1, (2, None, None), None))
        self.assertEqual(serialize(self.recover(root)), [2, 1])
        # 1 must not be the right child of 2.
        root = from_structure((2, None, (1, None, None)))
        self.assertEqual(serialize(self.recover(root)), [1, None, 2])

    def test_adjacent_inorder_swap(self):
        # One descent only: the two neighbours are the swapped pair.
        root = from_structure((2, (1, None, None), (4, (3, None, None), None)))
        swap_pair(root, 2, 3)  # keys 3 and 4
        self.assertEqual(serialize(self.recover(root)), [2, 1, 4, None, None, 3])

    def test_non_adjacent_inorder_swap(self):
        # Two descents, far apart in inorder (key 1 and key 4 of 0..5).
        root = build_valid_bst(6)
        swap_pair(root, 1, 4)
        self.recover(root)
        self.assertEqual(inorder_values(root), [0, 1, 2, 3, 4, 5])

    def test_root_and_leaf_swap(self):
        root = from_structure(
            (10, (5, (3, None, None), (7, None, None)), (15, None, None))
        )
        swap_pair(root, 0, 4)  # smallest key (a leaf) with the root key
        self.recover(root)
        self.assertEqual(inorder_values(root), [3, 5, 7, 10, 15])

    def test_inorder_neighbours_at_the_ends(self):
        root = build_valid_bst(8)
        swap_pair(root, 0, 1)
        self.recover(root)
        self.assertEqual(inorder_values(root), list(range(8)))
        root = build_valid_bst(8)
        swap_pair(root, 6, 7)
        self.recover(root)
        self.assertEqual(inorder_values(root), list(range(8)))

    def test_broken_trees_really_are_broken(self):
        # Guards the generator: exchanging two distinct keys must break the BST.
        for size in range(2, 9):
            for i, j in itertools.combinations(range(size), 2):
                root = build_valid_bst(size)
                swap_pair(root, i, j)
                with self.subTest(size=size, i=i, j=j):
                    self.assertFalse(range_check(root))

    def test_exhaustive_small_cases(self):
        for size in range(2, 7):
            for shape in all_shapes(size):
                for i, j in itertools.combinations(range(size), 2):
                    with self.subTest(size=size, i=i, j=j):
                        root = from_structure(fill_inorder(shape, range(size)))
                        swap_pair(root, i, j)

                        pairs = repairing_pairs(root)
                        self.assertEqual(len(pairs), 1, 'the repair must be unique')
                        first, second = pairs[0]
                        broken_first, broken_second = first.val, second.val

                        self.recover(root)
                        self.assertEqual(inorder_values(root), list(range(size)))
                        # The same two nodes were exchanged back.
                        self.assertEqual(first.val, broken_second)
                        self.assertEqual(second.val, broken_first)

    def test_random_small_cases_against_pair_oracle(self):
        rng = random.Random(990)
        for _ in range(200):
            size = rng.randint(2, 10)
            root = build_valid_bst(size, rng)
            original = inorder_values(root)
            i, j = rng.sample(range(size), 2)
            swap_pair(root, i, j)
            with self.subTest(size=size, i=i, j=j):
                pairs = repairing_pairs(root)
                self.assertEqual(len(pairs), 1, 'the repair must be unique')
                self.recover(root)
                self.assertEqual(inorder_values(root), original)

    def test_random_medium_cases_restore_the_original_tree(self):
        rng = random.Random(991)
        for _ in range(200):
            size = rng.randint(2, 60)
            values = sorted(rng.sample(range(-100_000, 100_000), size))
            root = balanced_from_sorted(values)
            expected = serialize(root)
            i, j = rng.sample(range(size), 2)
            swap_pair(root, i, j)
            with self.subTest(size=size, i=i, j=j):
                self.recover(root)
                self.assertEqual(inorder_values(root), values)
                self.assertEqual(serialize(root), expected)

    def test_constraint_sized(self):
        # 1000 nodes is the constraint maximum.
        rng = random.Random(992)
        size = 1000
        values = sorted(rng.sample(range(-2 ** 31, 2 ** 31), size))
        root = balanced_from_sorted(values)
        expected = serialize(root)
        i, j = rng.sample(range(size), 2)
        swap_pair(root, i, j)
        self.recover(root)
        self.assertEqual(inorder_values(root), values)
        self.assertEqual(serialize(root), expected)

        # A 1000-node right chain: 1000 stack frames if the walk recursed.
        chain = None
        for value in reversed(range(size)):
            chain = TreeNode(value, None, chain)
        swap_pair(chain, 0, size - 1)  # smallest and largest keys
        self.recover(chain)
        self.assertEqual(inorder_values(chain), list(range(size)))


if __name__ == '__main__':
    unittest.main()
