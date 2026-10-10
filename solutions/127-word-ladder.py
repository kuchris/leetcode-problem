# 127. Word Ladder
# https://leetcode.com/problems/word-ladder/
#
# BFS by levels over the word graph; the level counter is the number of words in
# the shortest sequence found so far. beginWord is level 1, and the first time
# endWord is met while expanding level d the answer is d + 1.
#
# Neighbours come from wildcard buckets: a word is stored under every key that
# replaces one of its letters with '*', so words differing in exactly one
# position share exactly one bucket. That keeps neighbour generation proportional
# to N * L instead of N * L * 26 (or N^2 pairwise comparisons).
#
# Invariant: a word is marked visited the moment it is pushed onto the next
# frontier, so it is expanded at most once -- and because BFS expands words in
# non-decreasing level order, that first level is already the shortest distance
# from beginWord.
#
# Time: O(N * L)   Space: O(N * L)   (N distinct words, L = len(beginWord))

class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: list[str]) -> int:
        words = set(wordList)
        if endWord not in words:
            return 0

        length = len(beginWord)
        buckets: dict[str, list[str]] = {}
        for word in words | {beginWord}:
            for i in range(length):
                buckets.setdefault(word[:i] + '*' + word[i + 1:], []).append(word)

        visited = {beginWord}
        frontier = [beginWord]
        distance = 1

        while frontier:
            next_frontier: list[str] = []
            for word in frontier:
                for i in range(length):
                    for neighbour in buckets[word[:i] + '*' + word[i + 1:]]:
                        if neighbour == endWord:
                            return distance + 1
                        if neighbour in visited:
                            continue
                        visited.add(neighbour)
                        next_frontier.append(neighbour)
            frontier = next_frontier
            distance += 1

        return 0
