# 146. LRU Cache
# https://leetcode.com/problems/lru-cache/
#
# Entry point: LRUCache
# LeetCode judges this problem through LRUCache, not Solution -- the template
# defines no Solution class, so a Solution here would never be instantiated.
#
# `OrderedDict` keeps keys in insertion order, which is exactly the recency
# order the cache needs: the leftmost key is the least recently used and the
# rightmost is the most recently used.
#
#   - get: a hit moves the key to the right end (it is now the most recent) and
#     returns its value; a miss returns -1 and changes nothing.
#   - put: move an existing key to the right end before overwriting it (a plain
#     assignment to an existing key keeps its old position), insert a new key at
#     the right end, then evict from the left end while the size exceeds the
#     capacity.
#
# Invariant: after every operation the mapping holds at most `capacity` keys in
# ascending recency order, so `popitem(last=False)` always removes the key that
# was used longest ago. Each operation only touches the two ends of the ordered
# mapping, so both are O(1) average time.
#
# Time: O(1) average per get and put   Space: O(capacity)

import collections


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.entries: "collections.OrderedDict[int, int]" = collections.OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.entries:
            return -1
        self.entries.move_to_end(key)
        return self.entries[key]

    def put(self, key: int, value: int) -> None:
        if key in self.entries:
            self.entries.move_to_end(key)
        self.entries[key] = value
        while len(self.entries) > self.capacity:
            self.entries.popitem(last=False)
