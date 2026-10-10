import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('57-insert-interval.py').Solution


def brute_force(intervals: list[list[int]], new_interval: list[int]) -> list[list[int]]:
    """Insert then merge, using a different sweep from the solution."""
    everything = sorted(
        [list(pair) for pair in intervals] + [list(new_interval)],
        key=lambda pair: (pair[0], pair[1]),
    )
    merged: list[list[int]] = []
    for start, end in everything:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def disjoint_lists(universe, max_size):
    """Every sorted list of pairwise non-overlapping intervals."""
    results = [[]]
    for size in range(1, max_size + 1):
        for combo in itertools.combinations(universe, size):
            ordered = sorted(combo)
            if all(ordered[i][1] < ordered[i + 1][0] for i in range(len(ordered) - 1)):
                results.append([list(pair) for pair in ordered])
    return results


class InsertIntervalTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().insert

    def test_official_examples(self):
        self.assertEqual(self.solve([[1, 3], [6, 9]], [2, 5]), [[1, 5], [6, 9]])
        self.assertEqual(
            self.solve([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]),
            [[1, 2], [3, 10], [12, 16]],
        )

    def test_empty_intervals(self):
        self.assertEqual(self.solve([], [5, 7]), [[5, 7]])

    def test_new_interval_before_everything(self):
        self.assertEqual(self.solve([[5, 7], [9, 10]], [1, 2]), [[1, 2], [5, 7], [9, 10]])

    def test_new_interval_after_everything(self):
        self.assertEqual(self.solve([[1, 2], [3, 4]], [10, 12]), [[1, 2], [3, 4], [10, 12]])

    def test_new_interval_swallows_everything(self):
        self.assertEqual(self.solve([[2, 3], [5, 6], [8, 9]], [1, 10]), [[1, 10]])

    def test_touching_endpoints_merge(self):
        self.assertEqual(self.solve([[1, 2], [5, 6]], [2, 5]), [[1, 6]])

    def test_input_is_not_modified(self):
        intervals = [[1, 3], [6, 9]]
        new_interval = [2, 5]
        original = [list(pair) for pair in intervals]
        self.solve(intervals, new_interval)
        self.assertEqual(intervals, original)
        self.assertEqual(new_interval, [2, 5])

    def test_maximum_size(self):
        intervals = [[4 * i, 4 * i + 1] for i in range(10000)]
        result = self.solve(intervals, [40000, 40001])
        self.assertEqual(result, intervals + [[40000, 40001]])

    def test_exhaustive_small_cases(self):
        universe = [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (3, 4)]
        candidates = disjoint_lists(universe, 3)
        new_intervals = [[a, b] for a in range(4) for b in range(a, 5)]
        for intervals in candidates:
            for new_interval in new_intervals:
                with self.subTest(intervals=intervals, newInterval=new_interval):
                    self.assertEqual(
                        self.solve([list(p) for p in intervals], list(new_interval)),
                        brute_force([list(p) for p in intervals], list(new_interval)),
                    )

    def test_randomised_cases(self):
        rng = random.Random(57)
        for _ in range(100):
            # The problem guarantees sorted, non-overlapping input, so build it
            # by walking a cursor forward: each new start must exceed the
            # previous end, otherwise two intervals would share a point.
            intervals = []
            cursor = 0
            while cursor < 40 and len(intervals) < 6:
                cursor += rng.randint(0, 4)
                start = cursor
                end = start + rng.randint(0, 3)
                intervals.append([start, end])
                cursor = end + 1
            start = rng.randint(0, 40)
            new_interval = [start, start + rng.randint(0, 5)]
            with self.subTest(intervals=intervals, newInterval=new_interval):
                self.assertEqual(
                    self.solve([list(p) for p in intervals], list(new_interval)),
                    brute_force([list(p) for p in intervals], list(new_interval)),
                )


if __name__ == '__main__':
    unittest.main()
