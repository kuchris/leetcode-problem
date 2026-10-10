# 130. Surrounded Regions
# https://leetcode.com/problems/surrounded-regions/
#
# A region of 'O' survives exactly when it touches the border, because only a
# border region can reach outside the board. So instead of testing each region
# for enclosure, flood-fill from every border 'O' and mark everything reachable
# with a temporary '#'; those cells belong to a free region.
#
# Invariant: after the fill, 'O' means "belongs to some region that touches no
# border" and '#' means "connected to the border". The final sweep therefore maps
# 'O' -> 'X' (captured) and '#' -> 'O' (restored), and no cell is ever visited
# twice because the mark replaces the letter on the way in.
#
# Time: O(m * n)   Space: O(m * n)   (the stack can hold every cell of a region)

class Solution:
    def solve(self, board: list[list[str]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """
        if not board or not board[0]:
            return

        rows, cols = len(board), len(board[0])
        stack = []

        for r in range(rows):
            for c in (0, cols - 1):
                if board[r][c] == 'O':
                    stack.append((r, c))
        for c in range(cols):
            for r in (0, rows - 1):
                if board[r][c] == 'O':
                    stack.append((r, c))

        while stack:
            r, c = stack.pop()
            if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != 'O':
                continue
            board[r][c] = '#'  # reachable from the border, never captured
            stack.append((r + 1, c))
            stack.append((r - 1, c))
            stack.append((r, c + 1))
            stack.append((r, c - 1))

        for r in range(rows):
            for c in range(cols):
                if board[r][c] == 'O':
                    board[r][c] = 'X'
                elif board[r][c] == '#':
                    board[r][c] = 'O'
