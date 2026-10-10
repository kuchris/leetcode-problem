import itertools
import random
import unittest

from _loader import load_solution

Solution = load_solution('56-merge-intervals.py').Solution


def brute_force(intervals: list[list[int]]) -> list[list[int]]:
    """Merge any overlapping pair repeatedly until nothing changes."""
    work = [list(pair) for pair in intervals]
    changed = True
    while changed:
        changed = False
        for i in range(len(work)):
            for j in range(i + 1, len(work)):
                if work[i][0] <= work[j][1] and work[j][0] <= work[i][1]:
                    merged = [
                        min(work[i][0], work[j][0]),
                        max(work[i][1], work[j][1]),
                    ]
                    work = [w for k, w in enumerate(work) if k not in (i, j)]
                    work.append(merged)
                    changed = True
                    break
            if changed:
                break
    return sorted(work)


class MergeIntervalsTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().merge

    def test_official_examples(self):
        self.assertEqual(
            self.solve([[1, 3], [2, 6], [8, 10], [15, 18]]),
            [[1, 6], [8, 10], [15, 18]],
        )
        self.assertEqual(self.solve([[1, 4], [4, 5]]), [[1, 5]])
        self.assertEqual(self.solve([[4, 7], [1, 4]]), [[1, 7]])

    def test_single_interval(self):
        self.assertEqual(self.solve([[1, 5]]), [[1, 5]])
        self.assertEqual(self.solve([[0, 0]]), [[0, 0]])

    def test_disjoint_intervals_are_unchanged(self):
        self.assertEqual(self.solve([[1, 2], [4, 5], [7, 8]]), [[1, 2], [4, 5], [7, 8]])

    def test_touching_endpoints_merge(self):
        self.assertEqual(self.solve([[1, 2], [2, 3]]), [[1, 3]])

    def test_nested_intervals_are_absorbed(self):
        self.assertEqual(self.solve([[1, 10], [2, 3], [4, 5]]), [[1, 10]])

    def test_identical_intervals_collapse(self):
        self.assertEqual(self.solve([[1, 4], [1, 4], [1, 4]]), [[1, 4]])

    def test_input_is_not_modified(self):
        intervals = [[1, 3], [2, 6]]
        original = [list(pair) for pair in intervals]
        self.solve(intervals)
        self.assertEqual(intervals, original)

    def test_maximum_size(self):
        intervals = [[2 * i, 2 * i + 1] for i in range(10000)]
        self.assertEqual(self.solve(intervals), intervals)

    def test_exhaustive_small_cases(self):
        universe = [[0, 0], [0, 1], [1, 1], [1, 2], [0, 2], [2, 2]]
        for size in range(1, 5):
            for intervals in itertools.product(universe, repeat=size):
                with self.subTest(intervals=intervals):
                    self.assertEqual(
                        self.solve([list(p) for p in intervals]),
                        brute_force([list(p) for p in intervals]),
                    )

    def test_randomised_cases(self):
        rng = random.Random(56)
        for _ in range(100):
            intervals = []
            for _ in range(rng.randint(1, 20)):
                start = rng.randint(0, 20)
                intervals.append([start, rng.randint(start, 25)])
            with self.subTest(intervals=intervals):
                self.assertEqual(self.solve(intervals), brute_force(intervals))


if __name__ == '__main__':
    unittest.main()
