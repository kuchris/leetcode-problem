# Q3. Longest Resilient Subarray II — Biweekly Contest 193
# https://leetcode.com/problems/longest-resilient-subarray-ii/
#
# 設子陣列總和為 S。刪除任一元素 x 後均可被 k 整除，代表 x % k == S % k。
# 因此所有元素必須有相同餘數 r，且長度 L 必須滿足 (L - 1) * r % k == 0。
# 掃描連續相同餘數的區段；長度由 1 逐一增加，所有候選長度都會被檢查。
# 即使目前整段不合法，較短的合法長度亦已在之前記錄。
# n = len(nums)。時間 O(n)，額外空間 O(1)。


class Solution:
    def resilientSubarray(self, nums: list[int], k: int) -> int:
        answer = 1
        previous = -1
        length = 0

        for value in nums:
            remainder = value % k
            if remainder == previous:
                length += 1
            else:
                length = 1
                previous = remainder

            if (length - 1) * remainder % k == 0:
                answer = max(answer, length)

        return answer
