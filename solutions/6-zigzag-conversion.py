# 6. Zigzag Conversion
# https://leetcode.com/problems/zigzag-conversion/
#
# Writing the zigzag and then reading it row by row is the same as assigning
# each character index i to a row and then concatenating the rows. The pattern
# repeats every cycle = 2 * numRows - 2 characters: the first numRows positions
# walk down the rows, and the remaining numRows - 2 walk back up.
#
# Time: O(n)   Space: O(n)

class Solution:
    def convert(self, s: str, numRows: int) -> str:
        if numRows == 1 or numRows >= len(s):
            return s

        cycle = 2 * numRows - 2
        rows: list[list[str]] = [[] for _ in range(numRows)]

        for index, char in enumerate(s):
            offset = index % cycle
            # Positions past the last row travel back up the zigzag.
            row = offset if offset < numRows else cycle - offset
            rows[row].append(char)

        return ''.join(''.join(row) for row in rows)
