# 30. Substring with Concatenation of All Words
# https://leetcode.com/problems/substring-with-concatenation-of-all-words/
#
# Every word has the same length L, so a valid window is exactly
# L * len(words) characters and can only start at one of L residue classes
# modulo L. For each residue, slide a window one word at a time and keep a
# Counter of the words currently inside it:
#
#   - a word that is not in `target` breaks the window, so restart just after it;
#   - an over-represented word shrinks the window from the left until the count
#     is legal again;
#   - once the window holds exactly len(words) legal words, its left edge is an
#     answer, and the window is then advanced by one word.
#
# Each word position enters and leaves the window at most once per residue, so
# the total work is linear in the number of word slots.
#
# Time: O(n * L)  (n = len(s); each of the n/L slots per residue is sliced once)
# Space: O(len(words) * L) for the counters

from collections import Counter


class Solution:
    def findSubstring(self, s: str, words: list[str]) -> list[int]:
        if not s or not words:
            return []

        word_length = len(words[0])
        word_count = len(words)
        if word_length * word_count > len(s):
            return []

        target = Counter(words)
        n = len(s)
        starts = []

        for offset in range(word_length):
            left = offset
            seen: Counter[str] = Counter()
            used = 0

            for right in range(offset, n - word_length + 1, word_length):
                word = s[right:right + word_length]

                if word not in target:
                    seen.clear()
                    used = 0
                    left = right + word_length
                    continue

                seen[word] += 1
                used += 1

                while seen[word] > target[word]:
                    seen[s[left:left + word_length]] -= 1
                    used -= 1
                    left += word_length

                if used == word_count:
                    starts.append(left)
                    seen[s[left:left + word_length]] -= 1
                    used -= 1
                    left += word_length

        return starts
