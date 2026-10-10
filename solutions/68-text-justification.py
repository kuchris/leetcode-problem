# 68. Text Justification
# https://leetcode.com/problems/text-justification/
#
# Two passes over the words. The first packs each line greedily: a word fits
# while the running letter count plus the minimum single spaces between the
# words already chosen stays within maxWidth.
#
# For a full line with more than one word, the leftover space is split across
# the gaps with divmod, and the first `extra` gaps receive one extra space,
# which is exactly the "left slots get more" rule. A single-word line and the
# final line cannot be stretched, so they are left-justified and padded on the
# right.
#
# Time: O(total characters)   Space: O(maxWidth) per line, plus the output

class Solution:
    def fullJustify(self, words: list[str], maxWidth: int) -> list[str]:
        lines: list[str] = []
        index = 0
        total_words = len(words)

        while index < total_words:
            start = index
            letters = 0
            # index - start is the number of gaps needed so far.
            while (
                index < total_words
                and letters + len(words[index]) + (index - start) <= maxWidth
            ):
                letters += len(words[index])
                index += 1

            line = words[start:index]
            if index == total_words or len(line) == 1:
                text = ' '.join(line)
                lines.append(text + ' ' * (maxWidth - len(text)))
                continue

            gaps = len(line) - 1
            base, extra = divmod(maxWidth - letters, gaps)
            parts = []
            for position in range(gaps):
                parts.append(line[position])
                parts.append(' ' * (base + (1 if position < extra else 0)))
            parts.append(line[-1])
            lines.append(''.join(parts))

        return lines
