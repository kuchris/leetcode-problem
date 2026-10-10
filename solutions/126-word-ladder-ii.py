# 126. Word Ladder II
# https://leetcode.com/problems/word-ladder-ii/
#
# Layered BFS over the word graph. Rather than the graph itself, the search keeps
# `parents[w]` = every word one level closer to beginWord that can precede w.
# Those reverse edges are enough to rebuild all shortest sequences by walking
# backwards from endWord.
#
# Neighbours come from wildcard buckets: a word is stored under every key that
# replaces one of its letters with '*', so two words differing in exactly one
# position share exactly one bucket and no 26-letter scan per word is needed.
#
# Invariant: a word enters `visited` only after its entire level has been
# expanded. Two different words of level L may both be predecessors of the same
# level-(L+1) word, and marking a word as seen when it is first discovered would
# silently drop half of the shortest paths. For the same reason the search stops
# only once the level containing endWord has been fully expanded.
#
# Time: O(N * L + total words in the answer)   Space: O(N * L + answer)
#   (N distinct words, L = len(beginWord); the answer is bounded by 10^5 words)

class Solution:
    def findLadders(self, beginWord: str, endWord: str, wordList: list[str]) -> list[list[str]]:
        words = set(wordList)
        if endWord not in words:
            return []

        length = len(beginWord)
        buckets: dict[str, list[str]] = {}
        for word in words | {beginWord}:
            for i in range(length):
                buckets.setdefault(word[:i] + '*' + word[i + 1:], []).append(word)

        parents: dict[str, list[str]] = {}
        visited = {beginWord}
        frontier = [beginWord]

        while frontier and endWord not in parents:
            next_frontier: list[str] = []
            for word in frontier:
                for i in range(length):
                    for neighbour in buckets[word[:i] + '*' + word[i + 1:]]:
                        if neighbour in visited:
                            continue
                        if neighbour in parents:
                            parents[neighbour].append(word)
                        else:
                            parents[neighbour] = [word]
                            next_frontier.append(neighbour)
            visited.update(next_frontier)
            frontier = next_frontier

        if endWord not in parents:
            return []

        # Restrict the rebuild to words that really lie on a shortest path to
        # endWord, so that a word reached one level early but leading nowhere is
        # never explored.
        useful = {endWord}
        stack = [endWord]
        while stack:
            word = stack.pop()
            for previous in parents.get(word, ()):  # beginWord has no parents
                if previous not in useful:
                    useful.add(previous)
                    stack.append(previous)

        children: dict[str, list[str]] = {}
        for word, previous_list in parents.items():
            if word in useful:
                for previous in previous_list:
                    children.setdefault(previous, []).append(word)

        paths: list[list[str]] = []
        path = [beginWord]

        def walk(word: str) -> None:
            if word == endWord:
                paths.append(path.copy())
                return
            for nxt in children.get(word, ()):
                path.append(nxt)
                walk(nxt)
                path.pop()

        walk(beginWord)
        paths.sort()
        return paths
