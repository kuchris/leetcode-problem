import itertools
import unittest

from _loader import load_solution

Solution = load_solution('40-combination-sum-ii.py').Solution


def brute_force(candidates: list[int], target: int) -> list[list[int]]:
    """Every subset (each index used at most once) summing to the target."""
    found = set()
    for size in range(1, len(candidates) + 1):
        for combo in itertools.combinations(candidates, size):
            if sum(combo) == target:
                found.add(tuple(sorted(combo)))
    return sorted(list(c) for c in found)


def normalise(combos: list[list[int]]) -> list[list[int]]:
    return sorted(sorted(c) for c in combos)


class CombinationSumIITests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().combinationSum2

    def test_official_examples(self):
        self.assertEqual(
            normalise(self.solve([10, 1, 2, 7, 6, 1, 5], 8)),
            [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]],
        )
        self.assertEqual(
            normalise(self.solve([2, 5, 2, 1, 2], 5)), [[1, 2, 2], [5]]
        )

    def test_no_duplicate_combinations_despite_repeats(self):
        result = self.solve([1, 1, 1, 1, 1], 3)
        self.assertEqual(normalise(result), [[1, 1, 1]])
        self.assertEqual(len(result), 1)

    def test_repeated_values_can_all_be_used(self):
        self.assertEqual(normalise(self.solve([2, 2, 2], 6)), [[2, 2, 2]])

    def test_repeated_values_beyond_the_target_are_excluded(self):
        self.assertEqual(self.solve([3, 3, 3], 5), [])

    def test_no_solution(self):
        self.assertEqual(self.solve([5, 6], 1), [])

    def test_maximum_candidate_count(self):
        candidates = [1] * 50 + [50] * 50
        result = self.solve(candidates, 50)
        self.assertEqual(normalise(result), normalise([[50], [1] * 50]))

    def test_exhaustive_small_cases(self):
        pools = [
            [1, 2], [1, 1, 2], [2, 2, 3, 3], [1, 2, 3, 4], [5, 5, 5], [1, 1, 1, 1],
        ]
        for candidates in pools:
            for target in range(1, 16):
                with self.subTest(candidates=candidates, target=target):
                    self.assertEqual(
                        normalise(self.solve(list(candidates), target)),
                        brute_force(list(candidates), target),
                    )


if __name__ == '__main__':
    unittest.main()
