#!/bin/bash
# 194. Transpose File
# https://leetcode.com/problems/transpose-file/
#
# awk keeps one accumulator per column: row[i] starts as the first field seen in
# column i, and every later row appends " " plus its own field, so row[i] ends up
# holding the i-th column joined by single spaces -- exactly the transposed row.
#
# `i in row` decides whether column i has been initialised yet, which is sturdier
# than testing NR == 1: a blank first line has no fields, so that test would leave
# a later append with a stray leading space. ncols tracks the widest row rather
# than reading NF at END time, because NF is 0 there when the file ends with a
# blank line and the transpose would vanish. The statement guarantees every row
# has the same number of columns; an empty file prints nothing.
#
# Time: O(r * c) for an r-row, c-column file   Space: O(c) for the accumulators

awk '
  {
    for (i = 1; i <= NF; i++)
      row[i] = (i in row) ? row[i] " " $i : $i
    if (NF > ncols) ncols = NF
  }
  END { for (i = 1; i <= ncols; i++) print row[i] }
' file.txt
