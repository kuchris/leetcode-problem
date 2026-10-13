# 187. Repeated DNA Sequences
# https://leetcode.com/problems/repeated-dna-sequences/
#
# Slide a 10-letter window over the string and keep two sets: `seen` for windows
# already met once and `repeated` for windows met at least twice. Because the
# window advances one character at a time, overlapping repeats are found
# naturally.
#
# Invariant: after processing the window starting at `start`, `seen` holds every
# distinct window starting at an index <= start and `repeated` holds exactly
# those that have occurred at least twice, so after the loop `repeated` is the
# answer. Strings shorter than 10 letters produce no window at all.
#
# Time: O(n * 10) = O(n)   Space: O(n) for the sets
# (A 20-bit rolling code -- 2 bits per letter -- would replace the slicing with
# O(1) per step; the slicing version is kept for readability.)

class Solution:
    def findRepeatedDnaSequences(self, s: str) -> list[str]:
        seen = set()
        repeated = set()
        for start in range(len(s) - 9):
            window = s[start:start + 10]
            if window in seen:
                repeated.add(window)
            else:
                seen.add(window)
        return list(repeated)
