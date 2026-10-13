# 166. Fraction to Recurring Decimal
# https://leetcode.com/problems/fraction-to-recurring-decimal/
#
# Long division, with the remainder recorded as the state of the division:
#
#   - The sign is negative exactly when the two inputs have opposite signs, and
#     the division itself is done on absolute values. A zero numerator is
#     special-cased to "0" so that 0 / -3 never prints "-0".
#   - `whole` and the first remainder come from one divmod of the absolute
#     values. While the remainder is non-zero, multiplying it by 10 and dividing
#     by the divisor produces the next decimal digit.
#   - There are fewer than |divisor| distinct remainders, so the process either
#     reaches remainder 0 (a terminating expansion) or repeats a remainder.
#     `seen[remainder]` stores where that remainder's digit was written; when a
#     remainder reappears, the digits from that position onwards are exactly the
#     repeating block, so they are wrapped in parentheses.
#
# Invariant: the digits in `fraction` are the true decimal digits of the exact
# rational, in order, and the map holds the first occurrence of each remainder.
# A terminating expansion therefore prints no parentheses; any other prints the
# transient part followed by one parenthesised cycle.
#
# Time: O(k)   Space: O(k)   (k = number of distinct remainders, so k < |denominator|)

class Solution:
    def fractionToDecimal(self, numerator: int, denominator: int) -> str:
        if numerator == 0:
            return '0'

        sign = '-' if (numerator < 0) != (denominator < 0) else ''
        remainder = abs(numerator)
        divisor = abs(denominator)

        whole, remainder = divmod(remainder, divisor)

        digits: list[str] = []
        seen: dict[int, int] = {}
        while remainder != 0 and remainder not in seen:
            seen[remainder] = len(digits)
            remainder *= 10
            digit, remainder = divmod(remainder, divisor)
            digits.append(str(digit))

        if remainder == 0:
            fraction = ''.join(digits)
        else:
            start = seen[remainder]
            fraction = ''.join(digits[:start]) + '(' + ''.join(digits[start:]) + ')'

        if not fraction:
            return sign + str(whole)
        return sign + str(whole) + '.' + fraction
