# 17. Letter Combinations of a Phone Number
# https://leetcode.com/problems/letter-combinations-of-a-phone-number/
#
# The answer is the Cartesian product of the letter sets of each digit, so
# build it incrementally: start with the single empty prefix and, for every
# digit, replace each prefix with its expansions. After k digits there are
# exactly the expected 4^k combinations, so the work is proportional to the
# output size.
#
# Time: O(4^n * n) where n = len(digits)   Space: O(4^n * n) for the output

LETTERS = {
    '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
    '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz',
}


class Solution:
    def letterCombinations(self, digits: str) -> list[str]:
        if not digits:
            return []

        combinations = ['']
        for digit in digits:
            combinations = [
                prefix + letter
                for prefix in combinations
                for letter in LETTERS[digit]
            ]
        return combinations
