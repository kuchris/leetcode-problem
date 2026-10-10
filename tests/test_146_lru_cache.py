"""Tests for 146. LRU Cache.

Oracle: ``DictModel``, a plain-dict re-implementation of the same contract. A
dict already preserves insertion order, so "mark as most recent" is a pop plus
re-insert and "evict the least recently used" is `next(iter(data))` — a
deliberately different implementation from the solution's ``OrderedDict``.
The cache is stateful, so every case builds a fresh instance and a fresh model.

Recency is checked behaviourally, never by peeking at the solution's internals:
each operation's return value is compared while both are replayed, and after
every random sequence the model's least-recently-used key is requested from both
sides until the cache drains, then every key of the universe is read back
through both. A misplaced key therefore shows up as a differing value.
"""

import random
import unittest

from _loader import load_solution

module = load_solution('146-lru-cache.py')
LRUCache = module.LRUCache

MAX_CAPACITY = 3000
MAX_KEY = 10 ** 4
MAX_VALUE = 10 ** 5


class DictModel:
    """Plain-dict LRU cache: insertion order doubles as recency order."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data: dict = {}

    def get(self, key: int) -> int:
        if key not in self.data:
            return -1
        value = self.data.pop(key)
        self.data[key] = value
        return value

    def put(self, key: int, value: int) -> None:
        if key in self.data:
            self.data.pop(key)
        self.data[key] = value
        while len(self.data) > self.capacity:
            del self.data[next(iter(self.data))]

    def order(self) -> list:
        """Keys from least to most recently used."""
        return list(self.data)


def replay(operations, arguments, capacity):
    """Run one operation sequence on a fresh cache and a fresh model."""
    cache = LRUCache(capacity)
    model = DictModel(capacity)
    results = []
    for name, argument in zip(operations, arguments):
        if name == 'get':
            actual = cache.get(argument[0])
            expected = model.get(argument[0])
        else:
            cache.put(argument[0], argument[1])
            model.put(argument[0], argument[1])
            actual = expected = None
        results.append((actual, expected))
    return cache, model, results


def read_through_in_model_order(test, cache, model, universe):
    """Read every resident key in the model's own recency order, then the rest.

    Both sides are read in the same order, so their recency states stay in step
    and a key that only one side evicted shows up as a differing value.
    """
    for key in list(model.order()):
        test.assertEqual(cache.get(key), model.get(key), f'reading key {key}')
    for key in universe:
        test.assertEqual(cache.get(key), model.get(key), f'reading key {key}')


class LRUCacheTests(unittest.TestCase):
    def test_official_example(self):
        operations = ["LRUCache", "put", "put", "get", "put", "get", "put",
                      "get", "get", "get"]
        arguments = [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
        capacity = arguments[0][0]
        cache, model, results = replay(operations[1:], arguments[1:], capacity)
        self.assertEqual([actual for actual, _ in results],
                         [None, None, 1, None, -1, None, -1, 3, 4])
        self.assertEqual([actual for actual, _ in results],
                         [expected for _, expected in results])
        self.assertEqual(model.order(), [3, 4])
        read_through_in_model_order(self, cache, model, [1, 2, 3, 4])

    def test_capacity_one_evicts_the_only_key(self):
        cache = LRUCache(1)
        cache.put(1, 10)
        self.assertEqual(cache.get(1), 10)
        cache.put(2, 20)
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(2), 20)
        # Overwriting the single key keeps it resident.
        cache.put(2, 30)
        self.assertEqual(cache.get(2), 30)
        # A read of a missing key must not evict anything.
        self.assertEqual(cache.get(99), -1)
        self.assertEqual(cache.get(2), 30)

    def test_get_refreshes_recency(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        self.assertEqual(cache.get(1), 1)      # 1 is now the most recent
        cache.put(3, 3)                        # so 2 is evicted, not 1
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(1), 1)
        self.assertEqual(cache.get(3), 3)

    def test_put_refreshes_recency_and_updates_the_value(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(1, 100)                      # key 1 becomes most recent
        cache.put(3, 3)                        # key 2 is evicted
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(1), 100)
        self.assertEqual(cache.get(3), 3)

    def test_miss_does_not_change_recency(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        self.assertEqual(cache.get(1), 1)
        self.assertEqual(cache.get(99), -1)    # miss: key 1 stays the newest
        cache.put(3, 3)                        # 2 goes, 1 stays
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(1), 1)

    def test_eviction_order_over_many_keys(self):
        cache = LRUCache(3)
        for key in range(1, 4):
            cache.put(key, key * 10)
        cache.get(1)                           # recency: 2, 3, 1
        cache.put(4, 40)                       # evicts 2
        self.assertEqual(cache.get(2), -1)
        cache.put(5, 50)                       # evicts 3
        self.assertEqual(cache.get(3), -1)
        self.assertEqual(cache.get(1), 10)
        self.assertEqual(cache.get(4), 40)
        self.assertEqual(cache.get(5), 50)

    def test_boundary_keys_and_values(self):
        cache = LRUCache(1)
        cache.put(0, 0)
        self.assertEqual(cache.get(0), 0)
        cache.put(MAX_KEY, MAX_VALUE)
        self.assertEqual(cache.get(0), -1)
        self.assertEqual(cache.get(MAX_KEY), MAX_VALUE)

    def test_entry_point_is_the_judged_class(self):
        # LeetCode instantiates LRUCache for this problem, so that is the only
        # class the file needs; it declares the entry point in its header and
        # tests/test_solution_conventions.py checks the declaration.
        self.assertFalse(hasattr(module, 'Solution'))
        self.assertTrue(callable(LRUCache))

    def test_random_sequences_against_the_model(self):
        rng = random.Random(1460)
        for case in range(300):
            capacity = rng.randint(1, 6)
            length = rng.randint(1, 60)
            universe = list(range(rng.randint(1, 9)))
            operations, arguments = [], []
            for _ in range(length):
                if rng.random() < 0.45:
                    operations.append('get')
                    arguments.append([rng.choice(universe)])
                else:
                    operations.append('put')
                    arguments.append([rng.choice(universe), rng.randint(0, 99)])
            with self.subTest(case=case, capacity=capacity, length=length):
                cache, model, results = replay(operations, arguments, capacity)
                for index, (actual, expected) in enumerate(results):
                    self.assertEqual(actual, expected, f'operation {index}')
                read_through_in_model_order(self, cache, model, universe)

    def test_random_sequences_with_wide_keys(self):
        rng = random.Random(1461)
        for case in range(40):
            capacity = rng.randint(1, 20)
            universe = rng.sample(range(MAX_KEY + 1), 30)
            operations, arguments = [], []
            for _ in range(200):
                if rng.random() < 0.5:
                    operations.append('get')
                    arguments.append([rng.choice(universe)])
                else:
                    operations.append('put')
                    arguments.append([
                        rng.choice(universe),
                        rng.randint(0, MAX_VALUE),
                    ])
            with self.subTest(case=case):
                cache, model, results = replay(operations, arguments, capacity)
                for index, (actual, expected) in enumerate(results):
                    self.assertEqual(actual, expected, f'operation {index}')
                read_through_in_model_order(self, cache, model, universe)

    def test_constraint_sized(self):
        # The stated maximum: capacity 3000, 2 * 10^5 get/put calls.
        rng = random.Random(1462)
        capacity = MAX_CAPACITY
        universe = list(range(MAX_KEY + 1))
        operations, arguments = [], []
        for _ in range(200_000):
            key = rng.choice(universe)
            if rng.random() < 0.5:
                operations.append('get')
                arguments.append([key])
            else:
                operations.append('put')
                arguments.append([key, rng.randint(0, MAX_VALUE)])
        cache, model, results = replay(operations, arguments, capacity)
        mismatches = [
            index for index, (actual, expected) in enumerate(results)
            if actual != expected
        ]
        self.assertEqual(mismatches, [])
        # The cache ended full, and every resident key matches the model.
        self.assertEqual(len(model.order()), capacity)
        read_through_in_model_order(
            self, cache, model, rng.sample(universe, 300)
        )


if __name__ == '__main__':
    unittest.main()
