# 169. Majority Element
# https://leetcode.com/problems/majority-element/
#
# Boyer-Moore voting, which answers in one pass with O(1) extra space (the
# stated follow-up). Keep a candidate value and a balance: an occurrence equal to
# the candidate raises the balance, any other value lowers it, and a balance of
# zero resets the candidate to the current value.
#
# Invariant: think of the balance as "unmatched copies of the candidate" after
# repeatedly cancelling a copy of the candidate against a copy of a different
# value. Cancelling one copy of each of two *distinct* values cannot change which
# value is the strict majority of the multiset, because a value that occurs more
# than half the time cannot have all of its copies cancelled -- every
# cancellation removes at most one copy of it and one copy of something else, and
# there are fewer than half as many of everything else. So after the whole array
# the surviving candidate is the majority. (With no strict majority the final
# balance can be zero and the candidate would be arbitrary, but the problem
# guarantees the majority exists.)
#
# Time: O(n)   Space: O(1)

class Solution:
    def majorityElement(self, nums: list[int]) -> int:
        candidate = nums[0]
        balance = 0
        for value in nums:
            if balance == 0:
                candidate = value
                balance = 1
            elif value == candidate:
                balance += 1
            else:
                balance -= 1
        return candidate
