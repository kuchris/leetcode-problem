# 66. Plus One
# https://leetcode.com/problems/plus-one/
#
# Adding one only ever changes a suffix of 9s: find the rightmost digit below 9,
# raise it by one, and every 9 after it becomes 0. If all digits are 9 the carry
# propagates past the front, and the answer is a 1 followed by the same number
# of zeros.
#
# Time: O(n)   Space: O(1)  (only the all-9s case allocates a new list)

class Solution:
    def plusOne(self, digits: list[int]) -> list[int]:
        for index in range(len(digits) - 1, -1, -1):
            if digits[index] < 9:
                digits[index] += 1
                return digits
            digits[index] = 0

        return [1] + digits
