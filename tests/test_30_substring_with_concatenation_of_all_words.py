import itertools
import random
import unittest
from collections import Counter

from _loader import load_solution

Solution = load_solution('30-substring-with-concatenation-of-all-words.py').Solution


def brute_force(s: str, words: list[str]) -> list[int]:
    """Test every start index by re-counting the words in its window."""
    if not words:
        return []
    word_length = len(words[0])
    span = word_length * len(words)
    target = Counter(words)
    starts = []
    for start in range(len(s) - span + 1):
        window = s[start:start + span]
        chunks = Counter(window[i:i + word_length] for i in range(0, span, word_length))
        if chunks == target:
            starts.append(start)
    return starts


class SubstringWithConcatenationTests(unittest.TestCase):
    def setUp(self):
        self.solve = Solution().findSubstring

    def test_official_examples(self):
        self.assertEqual(sorted(self.solve('barfoothefoobarman', ['foo', 'bar'])), [0, 9])
        self.assertEqual(self.solve('wordgoodgoodgoodbestword', ['word', 'good', 'best', 'word']), [])
        self.assertEqual(sorted(self.solve('barfoofoobarthefoobarman', ['bar', 'foo', 'the'])), [6, 9, 12])

    def test_words_longer_than_the_string(self):
        self.assertEqual(self.solve('ab', ['abc']), [])
        self.assertEqual(self.solve('', ['a']), [])

    def test_repeated_words_must_all_be_used(self):
        # "aaaa" is a valid window at every start that fits in "aaaaaa".
        self.assertEqual(sorted(self.solve('aaaaaa', ['aa', 'aa'])), [0, 1, 2])
        self.assertEqual(sorted(self.solve('aaaaa', ['aa', 'aa'])), [0, 1])
        self.assertEqual(self.solve('aaa', ['aa', 'aa']), [])

    def test_overlapping_candidates(self):
        # Windows starting at odd offsets read "ba" pairs, which is not a word.
        self.assertEqual(sorted(self.solve('abababab', ['ab', 'ab'])), [0, 2, 4])

    def test_unmatched_word_resets_the_window(self):
        self.assertEqual(self.solve('xxbarfooyy', ['foo', 'bar']), [2])

    def test_maximum_size(self):
        s = 'a' * 10000
        self.assertEqual(len(self.solve(s, ['a'] * 5000)), 5001)

    def test_exhaustive_small_cases(self):
        strings = ['']
        for size in range(1, 8):
            strings += [''.join(c) for c in itertools.product('ab', repeat=size)]
        word_sets = [['a'], ['b'], ['a', 'b'], ['aa'], ['a', 'a'], ['ab', 'ba'], ['a', 'a', 'b']]
        for s in strings:
            for words in word_sets:
                with self.subTest(s=s, words=words):
                    self.assertEqual(
                        sorted(self.solve(s, list(words))),
                        brute_force(s, list(words)),
                    )

    def test_randomised_cases(self):
        rng = random.Random(30)
        for _ in range(200):
            word_length = rng.randint(1, 3)
            vocabulary = ['a' * word_length, 'b' * word_length, 'ab'[:word_length]]
            words = [rng.choice(vocabulary) for _ in range(rng.randint(1, 3))]
            s = ''.join(rng.choice('ab') for _ in range(rng.randint(0, 18)))
            with self.subTest(s=s, words=words):
                self.assertEqual(
                    sorted(self.solve(s, list(words))), brute_force(s, list(words))
                )


if __name__ == '__main__':
    unittest.main()
