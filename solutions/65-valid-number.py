# 65. Valid Number
# https://leetcode.com/problems/valid-number/
#
# The grammar in the statement maps directly onto one regular expression, which
# is far less error-prone than a hand-rolled state machine:
#
#   [+-]?                      optional sign
#   ( \d+ \.? \d* | \. \d+ )   an integer, "digits.", "digits.digits", or ".digits"
#   ( [eE] [+-]? \d+ )?        an optional exponent, whose part must be an integer
#
# The decimal alternative requires at least one digit overall, so "." alone is
# rejected, and the exponent group requires at least one digit, so "1e" and
# "99e2.5" are rejected. fullmatch (rather than a "$"-anchored search) avoids
# the trailing-newline subtlety of "$".
#
# Time: O(n)   Space: O(1)

import re

PATTERN = re.compile(r'[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?')


class Solution:
    def isNumber(self, s: str) -> bool:
        return PATTERN.fullmatch(s) is not None
