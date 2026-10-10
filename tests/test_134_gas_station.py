"""Tests for 134. Gas Station.

Two oracles, and the faster one is itself validated against the slower one:

  - `simulation_valid_starts` is the definition: for every start, drive the
    circuit and keep the starts whose tank never goes negative. O(n^2), used on
    small inputs.
  - `prefix_valid_starts` computes the *set* of all valid starts in O(n) from
    prefix sums of the surplus over the doubled route plus a sliding-window
    minimum. It shares no idea with the greedy single pass under test.

The problem guarantees the answer is unique when a solution exists, so the
sweeps only assert equality for inputs with at most one valid start; inputs with
several are counted and skipped rather than asserted, since the guarantee
excludes them.
"""

import collections
import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('134-gas-station.py').Solution


def simulation_valid_starts(gas: list[int], cost: list[int]) -> list:
    """Every feasible start, by direct simulation of the circuit."""
    n = len(gas)
    valid = []
    for start in range(n):
        tank = 0
        for step in range(n):
            index = (start + step) % n
            tank += gas[index] - cost[index]
            if tank < 0:
                break
        else:
            valid.append(start)
    return valid


def prefix_valid_starts(gas: list[int], cost: list[int]) -> list:
    """Every feasible start, from prefix sums and a sliding-window minimum."""
    n = len(gas)
    surplus = [gas[index] - cost[index] for index in range(n)]
    prefix = [0] * (2 * n + 1)
    for step in range(2 * n):
        prefix[step + 1] = prefix[step] + surplus[step % n]

    valid = []
    window = collections.deque()
    for right in range(1, 2 * n):
        while window and prefix[window[-1]] >= prefix[right]:
            window.pop()
        window.append(right)
        start = right - n
        if start >= 0:
            while window[0] < start + 1:
                window.popleft()
            if prefix[window[0]] - prefix[start] >= 0:
                valid.append(start)
    return valid


class GasStationTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().canCompleteCircuit

    def test_official_examples(self):
        self.assertEqual(self.solve([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), 3)
        self.assertEqual(self.solve([2, 3, 4], [3, 4, 3]), -1)

    def test_single_station(self):
        self.assertEqual(self.solve([0], [0]), 0)
        self.assertEqual(self.solve([5], [5]), 0)
        self.assertEqual(self.solve([5], [0]), 0)
        self.assertEqual(self.solve([0], [1]), -1)
        self.assertEqual(self.solve([0], [10 ** 4]), -1)

    def test_exact_total_surplus(self):
        self.assertEqual(self.solve([3, 1, 1], [1, 2, 2]), 0)
        self.assertEqual(self.solve([1, 1, 3], [2, 2, 1]), 2)

    def test_deficit_everywhere(self):
        self.assertEqual(self.solve([0, 0, 0], [1, 1, 1]), -1)
        self.assertEqual(self.solve([1, 1], [2, 2]), -1)
        self.assertEqual(self.solve([1, 1, 1, 1], [2, 1, 1, 1]), -1)
        self.assertEqual(self.solve([10 ** 4] * 5, [10 ** 4] * 4 + [10 ** 4 + 1]), -1)

    def test_oracle_agrees_with_simulation(self):
        # The O(n) prefix oracle must agree with the O(n^2) simulation, or the
        # large cases below would be checking nothing.
        for size in range(1, 5):
            for gas in itertools.product(range(3), repeat=size):
                for cost in itertools.product(range(3), repeat=size):
                    with self.subTest(gas=gas, cost=cost):
                        self.assertEqual(prefix_valid_starts(list(gas), list(cost)),
                                         simulation_valid_starts(list(gas), list(cost)))

    def test_exhaustive_small_cases(self):
        checked = 0
        skipped_multiple = 0
        for size in range(1, 5):
            for gas in itertools.product(range(3), repeat=size):
                for cost in itertools.product(range(3), repeat=size):
                    gas, cost = list(gas), list(cost)
                    valid = simulation_valid_starts(gas, cost)
                    if len(valid) > 1:
                        # Excluded by the uniqueness guarantee.
                        skipped_multiple += 1
                        continue
                    with self.subTest(gas=gas, cost=cost):
                        expected = valid[0] if valid else -1
                        self.assertEqual(self.solve(gas, cost), expected)
                        checked += 1
        self.assertGreater(checked, 1000)
        self.assertGreater(skipped_multiple, 0)

    def test_randomised_cases(self):
        rng = random.Random(1340)
        for _ in range(400):
            size = rng.randint(1, 40)
            gas = [rng.randint(0, 20) for _ in range(size)]
            cost = [rng.randint(0, 20) for _ in range(size)]
            valid = prefix_valid_starts(gas, cost)
            answer = self.solve(gas, cost)
            with self.subTest(gas=gas, cost=cost):
                if not valid:
                    self.assertEqual(answer, -1)
                else:
                    # A valid start, and exactly it when the answer is unique.
                    self.assertIn(answer, valid)
                    if len(valid) == 1:
                        self.assertEqual(answer, valid[0])

    def test_randomised_deficit_cases(self):
        rng = random.Random(1341)
        for _ in range(100):
            size = rng.randint(1, 30)
            gas = [rng.randint(0, 3) for _ in range(size)]
            # Strictly more spent than collected everywhere, so the total is
            # negative and no start can work.
            cost = [value + rng.randint(1, 3) for value in gas]
            with self.subTest(size=size):
                self.assertEqual(self.solve(gas, cost), -1)
                self.assertEqual(prefix_valid_starts(gas, cost), [])

    def test_constraint_sized_unique_answer(self):
        # 10^5 stations: one long deficit, one station that covers the whole of
        # it, everything else neutral, so station 1 is the only possible start.
        size = 10 ** 5
        gas = [0] * size
        cost = [0] * size
        gas[1] = 9999
        cost[0] = 9999
        self.assertEqual(len(gas), size)

        valid = prefix_valid_starts(gas, cost)
        self.assertEqual(valid, [1])
        self.assertEqual(self.solve(gas, cost), 1)

    def test_constraint_sized_flat_and_deficit(self):
        size = 10 ** 5
        self.assertEqual(self.solve([0] * size, [0] * size), 0)
        self.assertEqual(self.solve([1] * size, [1] * size), 0)
        self.assertEqual(self.solve([10 ** 4] * size, [10 ** 4] * size), 0)
        self.assertEqual(self.solve([0] * size, [1] * size), -1)
        self.assertEqual(self.solve([1] * size, [0] * size), 0)

    def test_constraint_sized_random(self):
        rng = random.Random(1342)
        size = 10 ** 5
        for _ in range(3):
            gas = [rng.randint(0, 10 ** 4) for _ in range(size)]
            cost = [rng.randint(0, 10 ** 4) for _ in range(size)]
            valid = prefix_valid_starts(gas, cost)
            answer = self.solve(gas, cost)
            with self.subTest(total=sum(gas) - sum(cost)):
                if not valid:
                    self.assertEqual(answer, -1)
                else:
                    self.assertIn(answer, valid)
                    if len(valid) == 1:
                        self.assertEqual(answer, valid[0])


if __name__ == '__main__':
    unittest.main()
