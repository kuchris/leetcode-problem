# 168. Excel Sheet Column Title
# https://leetcode.com/problems/excel-sheet-column-title/
#
# Excel titles are bijective base 26: the digits A..Z have the values 1..26 and
# there is no zero digit, so after Z comes AA (27) rather than BA.
#
# Subtracting one before dividing turns the bijective system into the ordinary
# positional one: divmod(n - 1, 26) yields remainder (n - 1) % 26 in 0..25, which
# is the offset of the *last* letter from 'A', and quotient (n - 1) // 26, which
# is the column number of the remaining prefix under the same encoding. The
# digits therefore come out least-significant first and are reversed at the end.
#
# Invariant: at the top of each iteration `n` is the column number that the
# not-yet-emitted prefix must represent; the loop ends exactly when that prefix
# is empty (n == 0). The -1 is what makes 26 -> "Z" and 27 -> "AA" instead of the
# ordinary base-26 digits 26 -> "BA" / 27 -> "BB".
#
# Time: O(log_26 n)   Space: O(log_26 n) for the letter list

class Solution:
    def convertToTitle(self, columnNumber: int) -> str:
        letters: list[str] = []
        n = columnNumber
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            letters.append(chr(ord('A') + remainder))
        letters.reverse()
        return ''.join(letters)
