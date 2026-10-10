# 76. Minimum Window Substring
# https://leetcode.com/problems/minimum-window-substring/
#
# Sliding window driven by a "still missing" counter instead of rescanning
# counters:
#
#   - `need[c]` is how many more copies of c the current window requires;
#     it starts at the frequency of c in t and may go negative once the window
#     holds a surplus. `missing` is the number of distinct characters whose
#     need is still positive.
#   - `right` grows the window one character at a time. Taking a needed
#     character decrements `need[ch]` and retires one deficiency when it hits 0.
#   - While `missing == 0` the window is valid, so it is a candidate; then the
#     window is shrunk from the left. Giving back a character only increases
#     `need[out]`, and the moment that pushes it back to +1 the window loses a
#     required character and the shrink loop stops.
#
# Invariant: after each `right`, [left, right] is the shortest valid window
# ending at `right` that the previous shrink produced, and `best` is only
# replaced by a strictly shorter window, so among all minimum-length windows
# the earliest start wins -- the statement guarantees the answer is unique,
# so that is the expected answer.
#
# Time: O(m + n)   Space: O(1)   (m = len(s), n = len(t); the counter holds at
# most 52 letter keys, so it is bounded by the alphabet)

class Solution:
    def minWindow(self, s: str, t: str) -> str:
        need: dict[str, int] = {}
        for ch in t:
            need[ch] = need.get(ch, 0) + 1
        missing = len(need)

        left = 0
        best_start, best_end = 0, -1  # [best_start, best_end) half-open

        for right, ch in enumerate(s):
            if ch in need:
                need[ch] -= 1
                if need[ch] == 0:
                    missing -= 1

            while missing == 0:
                if best_end < 0 or right - left + 1 < best_end - best_start:
                    best_start, best_end = left, right + 1
                out = s[left]
                if out in need:
                    need[out] += 1
                    if need[out] > 0:
                        missing += 1
                left += 1

        if best_end < 0:
            return ''
        return s[best_start:best_end]
