"""Tests for 173. Binary Search Tree Iterator.

This problem is judged through ``BSTIterator`` (declared as the entry point in the
solution header), not through ``Solution``.

Oracle: materialise the *whole* inorder list up front with an iterative walk, then
replay the exact same operation script against that list with an index. The
iterator under test and the oracle therefore see the same sequence of
hasNext()/next() calls, and every returned value and boolean is compared
element-wise -- a fresh iterator is built for each script, so no state leaks
between cases.

Scripts are generated so that next() is only ever called while the oracle still
has values, which is the guarantee the statement gives. The constraint-sized
cases drain a 10^5-node balanced tree and both 10^5-node chains, and the stated
O(h) memory follow-up is measured with tracemalloc against the oracle's list.
"""

import random
import tracemalloc
import unittest

from _trees import TreeNode, build, load_tree_solution

Solution = load_tree_solution('173-binary-search-tree-iterator.py')
BSTIterator = Solution.BSTIterator


def inorder_values(root) -> list:
    """Iterative inorder: the oracle's materialised sequence."""
    values = []
    stack = []
    node = root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        values.append(node.val)
        node = node.right
    return values


def preorder_values(root) -> list:
    values = []
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        values.append(node.val)
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    return values


def balanced_bst(sorted_values) -> "TreeNode | None":
    if not sorted_values:
        return None
    middle = len(sorted_values) // 2
    return TreeNode(
        sorted_values[middle],
        balanced_bst(sorted_values[:middle]),
        balanced_bst(sorted_values[middle + 1:]),
    )


def chain_bst(size: int, side: str = 'right') -> "TreeNode | None":
    root = None
    if side == 'right':
        for value in reversed(range(size)):
            root = TreeNode(value, None, root)
    else:
        for value in range(size):
            root = TreeNode(value, root, None)
    return root


def random_bst(rng: random.Random, size: int) -> "TreeNode | None":
    """A BST built by inserting a permutation of distinct keys."""
    root = None
    for value in rng.sample(range(size * 10 + 1), size):
        if root is None:
            root = TreeNode(value)
            continue
        node = root
        while True:
            if value < node.val:
                if node.left is None:
                    node.left = TreeNode(value)
                    break
                node = node.left
            else:
                if node.right is None:
                    node.right = TreeNode(value)
                    break
                node = node.right
    return root


def all_shapes(size):
    if size == 0:
        yield None
        return
    for left_size in range(size):
        for left in all_shapes(left_size):
            for right in all_shapes(size - 1 - left_size):
                yield (left, right)


def fill_inorder(shape, values) -> "TreeNode | None":
    """Assign increasing `values` in inorder, which makes a valid BST."""
    iterator = iter(values)

    def ordered(node):
        if node is None:
            return None
        left, right = node
        left_subtree = ordered(left)
        value = next(iterator)
        right_subtree = ordered(right)
        return TreeNode(value, left_subtree, right_subtree)

    if shape is None:
        return None
    return ordered(shape)


def drain_script(node_count: int) -> list:
    """hasNext before every next(), plus a final hasNext()."""
    script = []
    for _ in range(node_count):
        script.append('has')
        script.append('next')
    script.append('has')
    return script


def random_script(rng: random.Random, node_count: int) -> list:
    script = []
    remaining = node_count
    while remaining > 0 or rng.random() < 0.3:
        if remaining > 0 and rng.random() < 0.6:
            script.append('next')
            remaining -= 1
        else:
            script.append('has')
        if remaining == 0 and rng.random() < 0.5:
            script.append('has')
            break
    script.append('has')
    return script


class BinarySearchTreeIteratorTests(unittest.TestCase):
    def replay(self, root, script):
        """Run the same script on the iterator and on the list oracle."""
        expected = inorder_values(root)
        iterator = BSTIterator(root)
        index = 0
        produced = []
        oracle = []
        for operation in script:
            if operation == 'has':
                produced.append(iterator.hasNext())
                oracle.append(index < len(expected))
            else:
                self.assertLess(index, len(expected),
                                'the script calls next() past the end')
                produced.append(iterator.next())
                oracle.append(expected[index])
                index += 1
        self.assertEqual(produced, oracle)
        return produced, index, expected

    def test_official_example(self):
        root = build([7, 3, 15, None, None, 9, 20])
        iterator = BSTIterator(root)
        produced = [iterator.next(), iterator.next(), iterator.hasNext(),
                    iterator.next(), iterator.hasNext(), iterator.next(),
                    iterator.hasNext(), iterator.next(), iterator.hasNext()]
        self.assertEqual(produced, [3, 7, True, 9, True, 15, True, 20, False])

    def test_single_node(self):
        root = TreeNode(1)
        iterator = BSTIterator(root)
        self.assertTrue(iterator.hasNext())
        self.assertEqual(iterator.next(), 1)
        self.assertFalse(iterator.hasNext())
        # hasNext stays False when called repeatedly.
        self.assertFalse(iterator.hasNext())

    def test_small_shapes(self):
        cases = [
            (build([1]), [1]),
            (build([2, 1]), [1, 2]),
            (build([1, None, 2]), [1, 2]),
            (build([3, 1, 2]), [1, 2, 3]),
            (build([2, 1, 3]), [1, 2, 3]),
        ]
        for root, expected in cases:
            with self.subTest(expected=expected):
                self.replay(root, drain_script(len(expected)))

    def test_chains(self):
        for size in (1, 2, 5, 50):
            for side in ('left', 'right'):
                root = chain_bst(size, side)
                with self.subTest(size=size, side=side):
                    produced, index, expected = self.replay(root, drain_script(size))
                    self.assertEqual(index, size)
                    self.assertEqual(expected, list(range(size)))

    def test_exhaustive_small_bsts(self):
        rng = random.Random(1730)
        for size in range(1, 7):
            for shape in all_shapes(size):
                root = fill_inorder(shape, range(size))
                with self.subTest(size=size, shape=shape):
                    self.replay(root, drain_script(size))
                    self.replay(root, random_script(rng, size))

    def test_random_trees_and_scripts(self):
        rng = random.Random(1731)
        for _ in range(200):
            size = rng.randint(1, 200)
            root = random_bst(rng, size)
            script = random_script(rng, size)
            with self.subTest(size=size):
                produced, index, expected = self.replay(root, script)
                self.assertEqual(len(expected), size)
                self.assertEqual(index, script.count('next'))

    def test_partial_iteration_then_stop(self):
        root = balanced_bst(list(range(1, 101)))
        iterator = BSTIterator(root)
        first_half = [iterator.next() for _ in range(50)]
        self.assertEqual(first_half, list(range(1, 51)))
        self.assertTrue(iterator.hasNext())
        self.assertEqual(iterator.next(), 51)

    def test_tree_is_not_modified(self):
        rng = random.Random(1732)
        for size in (1, 2, 10, 100, 500):
            root = random_bst(rng, size)
            before = preorder_values(root)
            self.replay(root, drain_script(size))
            with self.subTest(size=size):
                self.assertEqual(preorder_values(root), before)

    def test_constraint_sized(self):
        # 10^5 nodes is the constraint maximum.
        size = 100_000

        balanced = balanced_bst(list(range(size)))
        produced, index, expected = self.replay(balanced, drain_script(size))
        self.assertEqual(index, size)
        self.assertEqual(len(expected), size)
        self.assertEqual(produced[:3], [True, 0, True])
        self.assertEqual(produced[-1], False)

        # A right chain: h = 10^5, so the stack holds every ancestor.
        right_chain = chain_bst(size, 'right')
        _, index, expected = self.replay(right_chain, drain_script(size))
        self.assertEqual(index, size)
        self.assertEqual(expected, list(range(size)))

        # A left chain: the initial left spine is the whole tree.
        left_chain = chain_bst(size, 'left')
        _, index, expected = self.replay(left_chain, drain_script(size))
        self.assertEqual(index, size)
        self.assertEqual(expected, list(range(size)))

    def test_memory_is_proportional_to_the_height(self):
        # A balanced tree of 10^5 nodes has height 17, so the stack stays tiny,
        # while the oracle's materialised inorder list holds every value.
        size = 100_000
        root = balanced_bst(list(range(size)))

        tracemalloc.start()
        iterator = BSTIterator(root)
        total = 0
        while iterator.hasNext():
            total += iterator.next()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertEqual(total, size * (size - 1) // 2)

        tracemalloc.start()
        expected = inorder_values(root)
        _, oracle_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertEqual(len(expected), size)

        self.assertLess(peak, 100_000)
        self.assertGreater(oracle_peak, 500_000)
        self.assertLess(peak, oracle_peak // 5)


if __name__ == '__main__':
    unittest.main()
