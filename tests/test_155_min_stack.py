"""Tests for 155. Min Stack.

The oracle is a deliberately naive model: `PlainStackModel` keeps a plain Python
list and *recomputes* `min(items)` on every `getMin` call, so it shares neither
state nor invariant with the two-parallel-stacks implementation under test.

Both the model and the class under test are built through factories
(`run_operations` takes one), so every case -- and every step of the exhaustive
sweep -- starts from a fresh instance; a leaked or class-level stack cannot make a
later case pass.

Coverage: the official call sequence, every valid call sequence of length 1..5
over push/pop/top/getMin, randomised long sequences, the -2^31 / 2^31 - 1
boundaries, the documented parallel-stack invariant, and the 3 * 10^4-call
constraint maximum.
"""

import itertools
import random
import unittest

from _loader import load_solution

module = load_solution('155-min-stack.py')
MinStack = module.MinStack


class PlainStackModel:
    """Reference model: a plain list, minimum recomputed on every query."""

    def __init__(self):
        self.items = []

    def push(self, value: int) -> None:
        self.items.append(value)

    def pop(self) -> None:
        self.items.pop()

    def top(self) -> int:
        return self.items[-1]

    def getMin(self) -> int:
        return min(self.items)


def run_operations(factory, operations) -> list:
    """Run `(method, args)` pairs on a fresh object and collect the returns."""
    target = factory()
    results = []
    for method, args in operations:
        results.append(getattr(target, method)(*args))
    return results


def valid_sequences(pool, max_length: int, size: int = 0):
    """Every sequence of at most `max_length` pool operations that never queries
    an empty stack (the statement guarantees pop/top/getMin are only called on
    non-empty stacks)."""
    if max_length == 0:
        yield []
        return
    for method, args in pool:
        if method != 'push' and size == 0:
            continue
        new_size = size + 1 if method == 'push' else size - (1 if method == 'pop' else 0)
        for rest in valid_sequences(pool, max_length - 1, new_size):
            yield [(method, args)] + rest


PUSH_OPS = [('push', (value,)) for value in (-1, 0, 1)]
QUERY_OPS = [('pop', ()), ('top', ()), ('getMin', ())]
POOL = PUSH_OPS + QUERY_OPS


class MinStackTests(unittest.TestCase):
    def test_official_example(self):
        operations = [
            ('push', (-2,)),
            ('push', (0,)),
            ('push', (-3,)),
            ('getMin', ()),
            ('pop', ()),
            ('top', ()),
            ('getMin', ()),
        ]
        self.assertEqual(
            run_operations(MinStack, operations),
            [None, None, None, -3, None, 0, -2],
        )
        self.assertEqual(run_operations(MinStack, operations), run_operations(PlainStackModel, operations))

    def test_push_and_pop_return_none(self):
        stack = MinStack()
        self.assertIsNone(stack.push(4))
        self.assertIsNone(stack.push(5))
        self.assertIsNone(stack.pop())

    def test_single_element(self):
        for value in (-2 ** 31, -1, 0, 1, 2 ** 31 - 1):
            with self.subTest(value=value):
                stack = MinStack()
                stack.push(value)
                self.assertEqual(stack.top(), value)
                self.assertEqual(stack.getMin(), value)

    def test_minimum_is_restored_after_popping_it(self):
        stack = MinStack()
        for value in (5, 3, 7, 3):
            stack.push(value)
        self.assertEqual(stack.getMin(), 3)
        stack.pop()  # removes the second 3, the first one still pins the minimum
        self.assertEqual(stack.getMin(), 3)
        stack.pop()
        self.assertEqual(stack.getMin(), 3)
        stack.pop()  # removes the last 3
        self.assertEqual(stack.getMin(), 5)
        self.assertEqual(stack.top(), 5)

    def test_decreasing_and_increasing_sequences(self):
        stack = MinStack()
        for value in (4, 3, 2, 1, 0):
            stack.push(value)
            self.assertEqual(stack.getMin(), value)
        for expected in (1, 2, 3, 4):
            stack.pop()
            self.assertEqual(stack.getMin(), expected)

        stack = MinStack()
        for value in (0, 1, 2, 3, 4):
            stack.push(value)
            self.assertEqual(stack.getMin(), 0)
        for _ in range(4):
            stack.pop()
            self.assertEqual(stack.getMin(), 0)

    def test_all_equal_elements(self):
        stack = MinStack()
        for _ in range(50):
            stack.push(-7)
        self.assertEqual(stack.getMin(), -7)
        self.assertEqual(stack.top(), -7)
        for _ in range(49):
            stack.pop()
            self.assertEqual(stack.getMin(), -7)

    def test_boundary_values(self):
        stack = MinStack()
        stack.push(2 ** 31 - 1)
        self.assertEqual(stack.getMin(), 2 ** 31 - 1)
        stack.push(-2 ** 31)
        self.assertEqual(stack.getMin(), -2 ** 31)
        stack.push(0)
        self.assertEqual(stack.getMin(), -2 ** 31)
        stack.pop()
        stack.pop()
        self.assertEqual(stack.getMin(), 2 ** 31 - 1)
        self.assertEqual(stack.top(), 2 ** 31 - 1)

    def test_instances_are_independent(self):
        first, second = MinStack(), MinStack()
        first.push(5)
        first.push(3)
        second.push(9)
        second.push(8)
        self.assertEqual(first.getMin(), 3)
        self.assertEqual(second.getMin(), 8)
        second.pop()
        second.push(1)
        self.assertEqual(first.getMin(), 3)
        self.assertEqual(first.top(), 3)
        self.assertEqual(second.getMin(), 1)
        # A class-level container shared by every instance would show up here.
        self.assertIsNot(first._values, second._values)
        self.assertIsNot(first._minima, second._minima)

    def test_documented_parallel_stack_invariant(self):
        rng = random.Random(1550)
        stack = MinStack()
        model = PlainStackModel()
        for _ in range(600):
            if not model.items or rng.random() < 0.6:
                value = rng.randint(-5, 5)
                stack.push(value)
                model.push(value)
            else:
                stack.pop()
                model.pop()
            self.assertEqual(len(stack._values), len(stack._minima))
            self.assertEqual(stack._values, model.items)
            if model.items:
                self.assertEqual(stack._minima[-1], min(model.items))

    def test_exhaustive_call_sequences(self):
        checked = 0
        for length in range(1, 7):
            for operations in valid_sequences(POOL, length):
                with self.subTest(operations=operations):
                    self.assertEqual(
                        run_operations(MinStack, operations),
                        run_operations(PlainStackModel, operations),
                    )
                checked += 1
        # 23916 valid sequences of length 1..6 over three pushes and three queries.
        self.assertGreater(checked, 20000)

    def test_exhaustive_boundary_value_sequences(self):
        pool = [('push', (2 ** 31 - 1,)), ('push', (-2 ** 31,))] + QUERY_OPS
        for length in range(1, 5):
            for operations in valid_sequences(pool, length):
                with self.subTest(operations=operations):
                    self.assertEqual(
                        run_operations(MinStack, operations),
                        run_operations(PlainStackModel, operations),
                    )

    def test_randomised_sequences(self):
        rng = random.Random(1551)
        for _ in range(300):
            size = 0
            operations = []
            for _ in range(rng.randint(1, 60)):
                if size == 0:
                    method, args = 'push', (rng.randint(-50, 50),)
                else:
                    method, args = rng.choice(
                        [('push', (rng.randint(-50, 50),)), ('pop', ()), ('top', ()), ('getMin', ())]
                    )
                if method == 'push':
                    size += 1
                elif method == 'pop':
                    size -= 1
                operations.append((method, args))
            with self.subTest(operations=operations):
                self.assertEqual(
                    run_operations(MinStack, operations),
                    run_operations(PlainStackModel, operations),
                )

    def test_randomised_get_min_after_every_push(self):
        rng = random.Random(1552)
        for _ in range(100):
            values = [rng.randint(-20, 20) for _ in range(rng.randint(1, 40))]
            operations = []
            for value in values:
                operations.append(('push', (value,)))
                operations.append(('getMin', ()))
            with self.subTest(values=values):
                self.assertEqual(
                    run_operations(MinStack, operations),
                    run_operations(PlainStackModel, operations),
                )

    def test_entry_point_is_the_judged_class(self):
        # LeetCode instantiates MinStack for this problem, so that is the only
        # class the file needs; it declares the entry point in its header and
        # tests/test_solution_conventions.py checks the declaration.
        self.assertFalse(hasattr(module, 'Solution'))
        self.assertTrue(callable(MinStack))

    def test_constraint_sized_call_count(self):
        # Exactly 3 * 10^4 calls, the constraint maximum: 10^4 pushes, then a mix
        # that pops each pushed value exactly once.
        rng = random.Random(1553)
        operations = [('push', (rng.randint(-2 ** 31, 2 ** 31 - 1),)) for _ in range(10000)]
        operations += [('pop', ())] * 5000
        operations += [('getMin', ())] * 5000
        operations += [('top', ())] * 5000
        operations += [('pop', ())] * 5000
        self.assertEqual(len(operations), 30000)

        results = run_operations(MinStack, operations)
        self.assertEqual(results, run_operations(PlainStackModel, operations))
        self.assertEqual(results[:10000], [None] * 10000)
        self.assertEqual(results[-5000:], [None] * 5000)

    def test_constraint_sized_alternating(self):
        # Push, then query, then pop: the minimum has to move back up every time.
        operations = []
        for value in range(10000):
            operations.append(('push', (10000 - value,)))
            operations.append(('getMin', ()))
            operations.append(('pop', ()))
        self.assertEqual(len(operations), 30000)
        results = run_operations(MinStack, operations)
        self.assertEqual(results, run_operations(PlainStackModel, operations))
        self.assertEqual([result for result in results if result is not None],
                         list(range(10000, 0, -1)))


if __name__ == '__main__':
    unittest.main()
