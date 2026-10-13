#!/bin/bash
# 195. Tenth Line
# https://leetcode.com/problems/tenth-line/
#
# sed -n cancels sed's default "print every line", and the address 10 restricts
# the p command to the tenth input line only. When the file holds fewer than ten
# lines the address never matches, so sed prints nothing and exits 0 -- the answer
# to the statement's first note ("If the file contains less than 10 lines, what
# should you output?"). Reading stops at end of file; nothing is buffered.
#
# Time: O(n) to read the file once   Space: O(1)

sed -n '10p' file.txt
