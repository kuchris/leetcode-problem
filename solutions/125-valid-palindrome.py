# 125. Valid Palindrome
# https://leetcode.com/problems/valid-palindrome/
#
# Two pointers walk towards each other from both ends. A character is skipped
# only when it is not alphanumeric, and the first surviving pair that differs
# proves the filtered string is not a palindrome.
#
# Invariant: before each comparison, every character outside [left, right] has
# already been matched with its mirror image, so only the next surviving pair
# needs checking. The skip loops are written as `left < right` loops so that a
# run of punctuation is consumed in place instead of with an extra pass, and the
# empty filtered string (all punctuation) falls out of the loop as True.
#
# Time: O(n)   Space: O(1)   (n = len(s))

class Solution:
    def isPalindrome(self, s: str) -> bool:
        left, right = 0, len(s) - 1

        while left < right:
            while left < right and not s[left].isalnum():
                left += 1
            while left < right and not s[right].isalnum():
                right -= 1
            if s[left].lower() != s[right].lower():
                return False
            left += 1
            right -= 1

        return True
