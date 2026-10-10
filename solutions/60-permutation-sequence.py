# 60. Permutation Sequence
# https://leetcode.com/problems/permutation-sequence/
#
# Reading permutations in lexicographic order groups them by first digit: each
# choice of first digit accounts for (n - 1)! permutations. That makes the
# ranking a factorial number system, so the k-th permutation can be built
# directly instead of generating and discarding the first k - 1 of them.
#
# Convert k to zero-based, then for each remaining position take
# index = k // (remaining - 1)! and keep the remainder. The chosen digit is
# removed from the pool, because it can no longer appear later.
#
# Time: O(n^2)  (the digit pool is a list; n <= 9)   Space: O(n)

class Solution:
    def getPermutation(self, n: int, k: int) -> str:
        factorials = [1] * (n + 1)
        for value in range(1, n + 1):
            factorials[value] = factorials[value - 1] * value

        pool = [str(value) for value in range(1, n + 1)]
        k -= 1  # switch to a zero-based rank
        chosen = []

        for remaining in range(n, 0, -1):
            block = factorials[remaining - 1]
            index, k = divmod(k, block)
            chosen.append(pool.pop(index))

        return ''.join(chosen)
