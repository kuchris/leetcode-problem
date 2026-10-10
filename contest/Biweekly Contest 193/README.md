# Biweekly Contest 193 — Q1–Q4

Python 3 解法。題意及限制依本次對話提供的截圖整理。

| 題目 | 程式 | 核心方法 |
| --- | --- | --- |
| Q1 Maximum Product Pair With Target Sum | [Python](q1-maximum-product-pair-with-target-sum.py) | Hash map |
| Q2 Longest Resilient Subarray I | [Python](q2-longest-resilient-subarray-i.py) | 相同餘數區段 + gcd |
| Q3 Longest Resilient Subarray II | [Python](q3-longest-resilient-subarray-ii.py) | 相同餘數區段，線性掃描 |
| Q4 Minimize Inversions in a Prefix Tree | [Python](q4-minimize-inversions-in-a-prefix-tree.py) | Trie 分組 + subset DP |

Q1/Q2 求解內容不變，只是檔名統一為細楷 `q1`–`q4` 前綴，方便排序及與 Q3/Q4 一致。
Q2 改用索引迭代，避免 `nums[1:]` 複製陣列。
Q3/Q4 的 frontend problem ID 尚未核實，因此使用 contest 題號命名。
本次嘗試經 repository CLI 讀取 live problem 失敗，未核實 Q3/Q4 的 editor 方法名稱。
目前分別使用 `resilientSubarray` / `minInversions`；提交時請以 editor signature 為準。

## Q1 — Maximum Product Pair With Target Sum

設較大值為 `x`，另一值必須是 `target - x`，而嚴格大小要求等價於
`2 * x > target`。先用 hash map 記錄每個值的一個 index，再找出符合條件且
complement 存在的最小 `x`。

乘積為 `x * (target - x)`。在 `x > target / 2` 的範圍內，它會隨 `x` 增加而
下降，所以最小可行 `x` 給出最大乘積，負數亦適用。因為兩個值必定不同，
兩個 index 也必定不同。沒有可行值就回傳 `[-1, -1]`。

- 時間：expected `O(n)`，`n = len(nums)`。
- 額外空間：`O(n)`。

## Q2 / Q3 — Longest Resilient Subarray

設子陣列總和為 `T`，刪除任一元素 `x` 後均可被 `k` 整除，等價於
`x % k == T % k`。因此所有元素都必須有相同餘數 `r`。
長度為 `L` 時，刪除任一元素後的餘數為 `((L - 1) * r) % k`。

所以合法的充分必要條件是：

1. 所有元素對 `k` 的餘數相同。
2. `(L - 1) * r % k == 0`。

**Q2 的現有實作：** 對每段相同餘數的區段，令 `step = k // gcd(r, k)`。
合法長度為 `1, 1 + step, 1 + 2 * step, ...`；區段長度為 `L` 時，最大合法長度是
`L - (L - 1) % step`。`r == 0` 時 `step == 1`，所有長度都合法。

**Q3 的實作：** 掃描時維護目前區段長度，直接檢查 `(length - 1) * r % k == 0`。
區段長度逐一經過 `1..L`，因此每個可能的合法長度都會被檢查；不需要枚舉起點。
Q3 只是將陣列長度上限由 2,500 增至 100,000，線性掃描仍適用。

- Q2：通常在題目整數範圍內視為 `O(n)` 時間；若計入 Euclidean gcd 的步數，
  為 `O(n + R log k)`，`R` 是相同餘數區段數。額外空間 `O(1)`。
- Q3：時間 `O(n)`，額外空間 `O(1)`。

## Q4 — Minimize Inversions in a Prefix Tree

Preorder 必須完成一個 child subtree 後才走另一個，因此每個 child subtree
會佔據一個連續區塊。固定這些區塊的前後次序後，它們之間的 inversion 數量，
不受各自內部遍歷次序影響，故可以獨立最佳化每個子樹。

### 1. 依 target 次序建立隱式 trie

`solve(order, depth)` 的 `order` 是此子樹所有 word indices，保持它們在 `target`
中的次序。以 `words[index][depth]` 分組便得到 children。

若某個 word 的長度等於 `depth`，它就是目前節點的標記。Preorder 必須先輸出它，
因此所有在 `target` 中比它早出現的後代都會形成 inversion。掃描時已記錄的
`labels` 數量正好就是這項固定成本。這亦處理了某個完整 word 是另一 word 前綴的情況。

### 2. 計算 children 之間的成本

`cost[g][h]` 是將 child `g` 整段排在 child `h` 之前的 inversion 數量。
按 target 次序掃描 group labels，遇到 `g` 時，之前每個 `h` 都會在這個排列下
形成 inversion，故加上 `seen[h]`。對角線的數值不會用於 DP。

### 3. Subset DP 選擇排列

`dp[mask]` 表示只排列 mask 中 children 的最小跨子樹成本。
若選擇 child `g` 第一個，令 `rest = mask` 移除 `g`：

```text
extra[g][rest] = sum(cost[g][h] for h in rest)
dp[mask] = min(extra[g][rest] + dp[rest] for g in mask)
dp[0] = 0
```

預先用最低位元遞推計算所有 `extra`，每個轉移便是常數時間。
最後加上所有 children 的內部最小成本，以及標記節點的固定成本。

**正確性：** 任意一對 word 的 inversion，若兩者是祖先／後代關係，就在祖先的
標記節點計入固定成本；否則就在它們最低共同祖先的跨子樹成本中計入。
每一對只會計算一次。DP 枚舉所有可能第一個 child，歸納可得最小排列成本。

**複雜度：** 設 `n = len(words)`、`S = sum(map(len, words))`、alphabet size `A = 10`。
每個節點若有 `m` 個 words、`d` 個 children，計數需 `O(d*m)`，DP 需 `O(d*2**d)`。
全樹的總計數成本為 `O(A*S)`。有分支節點的 `sum(d - 1)` 最多為 `n - 1`，
因此 DP 總成本上界為 `O(n*2**A)`。總時間 `O(A*S + n*2**A)`，
額外空間 `O(S + A*2**A)`；字串最長 20，遞迴深度最多 21。

## 本地驗證

從 repository root 執行：

```powershell
python -m unittest discover -s tests -p 'test_101204_maximum_product_pair_with_target_sum.py' -v
python -m unittest discover -s tests -p 'test_101198_longest_resilient_subarray_i.py' -v
python -m unittest discover -s tests -p 'test_biweekly_193_q3_q4.py' -v
```

Q1/Q2 沿用既有 examples、edge cases、oracle 及大輸入測試。
Q3 以逐一刪除元素的定義作 brute-force oracle，並測試長度 100,000。
Q4 小樹直接枚舉所有 child permutations 及完整 traversal 作 oracle，
亦包含完整前綴鏈、10 個 children、輸入不變及 10,000 個 words 的測試。
以上屬本地驗證，並非 LeetCode judge 的 Accepted 結果。
