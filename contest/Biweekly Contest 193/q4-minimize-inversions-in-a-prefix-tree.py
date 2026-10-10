# Q4. Minimize Inversions in a Prefix Tree — Biweekly Contest 193
# https://leetcode.com/problems/minimize-inversions-in-a-prefix-tree/
#
# 每個 child subtree 在 preorder 中必定是完整的一段，可獨立最佳化內部次序。
# cost[g][h] 表示先走 g 再走 h 所產生的跨子樹 inversions。
# 每個節點最多 10 個 children，以 subset DP 找出最小成本排列。
# 已標記節點必須先於所有後代輸出；它與後代的 inversions 是固定成本。
# 依 target 次序、下一個字元遞迴分組，即可建立隱式 trie。
#
# n = len(words)，S = 所有字串長度總和，A = 10。
# 時間 O(A*S + n*2**A)，額外空間 O(S + A*2**A)。遞迴深度最多 21。
# 方法名稱沿用對話中的 minInversions；如 LeetCode editor 不同，請改名。


class Solution:
    def minInversions(self, words: list[str], target: list[int]) -> int:
        def solve(order: list[int], depth: int) -> int:
            # order 保持 target 次序，只包含目前子樹的 word indices。
            groups: list[list[int]] = []
            group_id: dict[str, int] = {}
            labels: list[int] = []
            answer = 0

            for index in order:
                if len(words[index]) == depth:
                    # 此 word 在 preorder 必須最先輸出。
                    # target 中在它之前的後代，每個均產生一個 inversion。
                    answer += len(labels)
                    continue

                char = words[index][depth]
                if char not in group_id:
                    group_id[char] = len(groups)
                    groups.append([])

                g = group_id[char]
                groups[g].append(index)
                labels.append(g)

            for group in groups:
                answer += solve(group, depth + 1)

            d = len(groups)
            if d <= 1:
                return answer

            cost = [[0] * d for _ in range(d)]
            seen = [0] * d
            for g in labels:
                for h in range(d):
                    cost[g][h] += seen[h]
                seen[g] += 1

            size = 1 << d
            # extra[g][mask] = sum(cost[g][h] for h in mask)
            extra = [[0] * size for _ in range(d)]
            for g in range(d):
                for mask in range(1, size):
                    bit = mask & -mask
                    h = bit.bit_length() - 1
                    extra[g][mask] = extra[g][mask ^ bit] + cost[g][h]

            dp = [0] * size
            for mask in range(1, size):
                best = float("inf")
                bits = mask
                while bits:
                    bit = bits & -bits
                    g = bit.bit_length() - 1
                    rest = mask ^ bit
                    # 將 g 排第一，再接上 rest 的最佳排列。
                    best = min(best, extra[g][rest] + dp[rest])
                    bits ^= bit
                dp[mask] = best

            return answer + dp[-1]

        return solve(target, 0)
