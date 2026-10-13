#!/bin/bash
# 192. Word Frequency
# https://leetcode.com/problems/word-frequency/
#
# Tokenise with tr: every whitespace character becomes a newline, so one word sits
# on each line. `grep -v '^$'` drops the empty lines a leading or trailing space
# would create -- without it `uniq -c` counts the empty string as a word. Then
# `sort | uniq -c` collapses identical words into "count word" lines.
#
# The second sort is the answer's order: field 1 is the count, descending, and
# field 2 breaks a tie by word. The statement guarantees the counts are unique
# ("Don't worry about handling ties"), so the tie-break never fires on the judge's
# data; it only makes the output deterministic instead of depending on sort's
# last-resort whole-line comparison.
#
# Time: O(n log n) for n word occurrences (the two sorts dominate)   Space: O(n)

tr -s '[:space:]' '\n' < words.txt \
  | grep -v '^$' \
  | LC_ALL=C sort \
  | uniq -c \
  | LC_ALL=C sort -k1,1nr -k2,2 \
  | awk '{ print $2, $1 }'
