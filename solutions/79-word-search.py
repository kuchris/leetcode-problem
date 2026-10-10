# 79. Word Search
# https://leetcode.com/problems/word-search/
#
# Depth-first search from every cell that could start the word. The path is
# tracked by temporarily overwriting a visited cell with '' and restoring the
# original letter on the way out, which is what keeps the "same cell may not be
# used twice" rule exact while leaving the board unchanged afterwards.
#
# Invariant: `search(r, c, index)` is called only when the path so far spells
# word[:index] along adjacent cells, and it reports whether that path extends to
# the whole word from cell (r, c).
#
# Time: O(m * n * 3^L)   Space: O(L)   (m x n board, L = len(word); each step
# after the first has at most 3 unvisited neighbours)

class Solution:
    def exist(self, board: list[list[str]], word: str) -> bool:
        rows, cols = len(board), len(board[0])

        def search(r: int, c: int, index: int) -> bool:
            if index == len(word):
                return True
            if r < 0 or r >= rows or c < 0 or c >= cols:
                return False
            if board[r][c] != word[index]:
                return False

            board[r][c] = ''  # mark this cell as used on the current path
            found = (
                search(r + 1, c, index + 1)
                or search(r - 1, c, index + 1)
                or search(r, c + 1, index + 1)
                or search(r, c - 1, index + 1)
            )
            board[r][c] = word[index]  # backtrack

            return found

        for r in range(rows):
            for c in range(cols):
                if search(r, c, 0):
                    return True
        return False
