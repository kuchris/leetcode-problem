#!/bin/bash
# 193. Valid Phone Numbers
# https://leetcode.com/problems/valid-phone-numbers/
#
# One -E pattern covers both formats: either a "(ddd) " prefix or a "ddd-" prefix,
# followed by ddd-dddd. The ^ and $ anchors make the pattern match the whole line,
# which is the trap in this problem: without them a number embedded in other text
# ("call 987-123-4567 now") is printed even though it is not a valid entry.
# [0-9] and {n} are used instead of \d because \d is a PCRE extension, not ERE.
#
# `|| true` keeps the script's exit status 0 when no line matches: grep exits 1 on
# an empty result and a shell submission should not look like a failed run. It
# does not change stdout, which is empty either way.
#
# Time: O(total characters of file.txt)   Space: O(1)

grep -E '^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$' file.txt || true
