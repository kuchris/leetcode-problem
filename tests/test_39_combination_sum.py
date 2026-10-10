import itertools
import unittest

from _loader import load_solution

Solution = load_solution('39-combination-sum.py').Solution


def brute_force(candidates: list[int], target: int) -> list[list[int]]:
    """Every multiset of candidates (any size) whose sum is the target."""
    found = []
    smallest = min(candidates)
    for size in range(1, target // smallest + 1):
        for combo in itertools.combinations_with_replacement(candidates, size):
            if sum(combo) == target:
                found.append(sorted(combo))
    return sorted(found)


def normalise(combos: list[list[int]]) -> list[list[int]]:
    return sorted(sorted(c) for c in combos)


class CombinationSumTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().combinationSum

    def test_official_examples(self):
        self.assertEqual(
            normalise(self.solve([2, 3, 6, 7], 7)), [[2, 2, 3], [7]]
        )
        self.assertEqual(
            normalise(self.solve([2, 3, 5], 8)), [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
        )
        self.assertEqual(self.solve([2], 1), [])

    def test_single_candidate_reused(self):
        self.assertEqual(self.solve([1], 4), [[1, 1, 1, 1]])

    def test_target_reached_exactly_by_one_candidate(self):
        self.assertEqual(normalise(self.solve([3, 5], 15)), [[3, 3, 3, 3, 3], [5, 5, 5]])

    def test_no_duplicate_combinations(self):
        result = self.solve([2, 3, 4, 7], 12)
        self.assertEqual(len(result), len({tuple(sorted(c)) for c in result}))

    def test_maximum_candidate_count(self):
        candidates = list(range(2, 32))
        result = self.solve(candidates, 40)
        self.assertTrue(all(sum(c) == 40 for c in result))
        self.assertEqual(len(result), len({tuple(sorted(c)) for c in result}))

    def test_exhaustive_small_cases(self):
        pools = [[2, 3], [2, 3, 5], [1, 2, 3], [2, 4, 6], [3, 7, 11], [5]]
        for candidates in pools:
            for target in range(1, 21):
                with self.subTest(candidates=candidates, target=target):
                    self.assertEqual(
                        normalise(self.solve(list(candidates), target)),
                        brute_force(list(candidates), target),
                    )


if __name__ == '__main__':
    unittest.main()
