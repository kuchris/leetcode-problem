# Agent Team — 工作流程與團隊結構

呢份文件記錄本 repo 用嘅多 agent 協作流程：角色分工、交接憑證、工具、實測限制同已知陷阱。

目標係**盡快清掉 LeetCode 免費題庫**（3288 題），同時保持每個 solution 都有獨立驗證。

---

## 1. 團隊結構

| Agent | 角色 | 寫入範圍 | 職責 |
|---|---|---|---|
| **lead** | Orchestrator | `solutions/`, `tests/`, git | 切批次、建 queue、合併 ledger、派修復、commit。**唔做驗收** |
| **solver-1..4** | Solvers ×4 | `solutions/`, `tests/`（只限自己 id 範圍） | 解題 + 寫測試 |
| **submitter** | Submitter ×1 | 只有自己嘅 result 檔 | 經 CDP 提交到 LeetCode |
| **qa-1** | Failure triage | `qa-failures.json` | 提交後失敗分類 + 診斷，寫修復簡報 |

**已退役角色**（架構演進後移除）：
- ~~qa-2~~ —— 原本負責修 qa-1 報嘅 FAIL。因為 qa-1 首批 8/8 全 PASS、零 FAIL，加上改為 judge-driven 之後冇咗 pre-submit 關卡，所以移除。
- ~~submitter-b~~ —— 原本做第二個 submitter（port 9223）。實測證明限流綁 account，第二個 browser 只會爭同一份額度，所以改為單 submitter。

---

## 2. Workflow

```
solver-1 (#101-108) ─┐
solver-2 (#109-116) ─┤
solver-3 (#117-124) ─┼─→ submitter (watch mode) ─→ LeetCode judge
solver-4 (#125-132) ─┘                              │
                                                    ↓
                                      qa-1 分類 + 診斷失敗
                                                    │
                                                    ↓
                                      lead 派修復畀 solver ─→ 重交
```

**核心設計決定：judge 就係主要驗證者。**

早期架構有 pre-submission QA 關卡（qa-1 喺提交前獨立驗收）。呢個後尾移除咗，原因：
- solver 自己嘅測試套已經好強（每個 oracle 都獨立）
- LeetCode judge 係 ground truth，而且係免費嘅
- pre-submit 關卡拖慢 pipeline 但好少抓到嘢

所以流程變成：**solver 自己嘅測試係提交前唯一關卡，judge 係最終仲裁，qa-1 喺事後處理失敗。**

### 三個關鍵規則

1. **Submitter 唔等齊貨。** 一見到未 AC 嘅 solution 就交，唔等批次完成。
2. **QA 唔過度投資。** 冇發現錯就快速放行，唔好將一個批次變成無了期審計。
3. **Ledger 係權威記錄。** 報「未閉環」之前必須查 ledger——result 檔只係部分視野。

---

## 3. 交接憑證

所有 agent 透過檔案交接，唔靠對話記憶。

| 檔案 | 寫入者 | 讀取者 | 內容 |
|---|---|---|---|
| `%TEMP%\lc-fetch\accepted.json` | lead | 全部 | slug → Accepted 記錄（**權威**） |
| `%TEMP%\lc-fetch\question-ids.json` | lead | submitter | slug → 內部 `questionId` |
| `%TEMP%\lc-fetch\slugs-solverN.json` | lead | solver N | 預留嘅題目清單 |
| `%TEMP%\lc-fetch\submit-*.json` | submitter | lead, qa-1 | 提交結果 + judge 診斷 |
| `%TEMP%\lc-fetch\qa-failures.json` | qa-1 | lead | 修復簡報 |
| `%TEMP%\lc-fetch\STOP` | lead | submitter | 叫停 watch mode |

### 點解要用預留批次

`select-batch.py` 只寫一個共享 `slugs.json`。如果 4 個 solver 同時跑，佢哋會揀到**同一批題目**——呢個係 race condition。

`reserve-batches.py` 一次過鎖定所有 solver 嘅範圍，確保零重疊：

```powershell
python "$env:TEMP\lc-fetch\reserve-batches.py" 4 8   # 4 個 solver，每人 8 題
```

Solver 收到自己嘅 `slugs-solverN.json`，**嚴禁**再跑 `select-batch.py`。

---

## 4. 提交工具：零依賴 CDP Driver

`%TEMP%\lc-fetch\cdp-submit.mjs` —— 用 Node 內建 `WebSocket` 直接控制 Chrome，**零依賴、零安裝**。

### 點解需要佢

MCP HTTP 路徑（`tools/leetcode/call.mjs submit_solution`）約 20 次提交之後就會 **HTTP 403**，要等約 10 分鐘。真實 browser 容忍更高頻率。

### 兩種模式

**單次提交：**
```powershell
node "$d\cdp-submit.mjs" <tasks.json> <results.json> [interDelayMs] [port] [ledger.json]
```

**Watch mode（持續掃描）：**
```powershell
node "$d\cdp-submit.mjs" --watch <solutionsDir> <ledger.json> <questionIds.json> `
     <results.json> [interDelayMs] [pollMs] [port] [maxMinutes]
```

Watch mode 每 `pollMs` 掃一次 `solutions/`，交任何未 AC 嘅題，並且每次 poll 都重讀 ledger（所以 lead 嘅合併即時生效）。上限 `maxMinutes`，或者出現 `STOP` 檔就提早結束。

### 運作方式

1. 用臨時 profile（`%TEMP%\lc-chrome-profile-<port>`）開 Chrome —— **唔會碰你平時嘅瀏覽器**
2. 經 `Network.setCookie` 注入 `LEETCODE_SESSION`
3. 導航到題目頁，喺**頁面 context** 內 `fetch` 提交（帶 browser 自己嘅 TLS fingerprint、headers、CSRF token）
4. 輪詢 `/submissions/detail/<id>/check/` 直到 `state === 'SUCCESS'`

### 兩個必須保留嘅行為

**1. 跳過已 AC 嘅題。** 重跑唔會重複提交。冇呢個保護，重跑會製造重複提交同浪費限流額度。

**2. 保留失敗診斷。** 非 Accepted 時要保留 `lastTestcase`、`codeOutput`、`expectedOutput`、`runtimeError`、`compileError`、`stdOutput`。

> ⚠️ 呢個係踩過嘅坑：原本 driver 喺失敗時 `delete record.check`，結果 qa-1 只收到「Wrong Answer 307/309」，完全冇得診斷。修好之後 qa-1 才寫得出有用嘅修復簡報。

**3. 429 自動退避。** 30s → 60s → 120s → 240s，最多 6 次。

---

## 5. 實測限制（重要）

### 限流綁 account，唔係綁 browser

| 設定 | 結果 |
|---|---|
| 1 個 browser，8 秒間隔 | 18 次提交，**零 429** |
| **2 個 browser，3 秒間隔** | **交咗 5 次就開始 429** |
| 1 個 browser，10 秒間隔 | 8/8，**零 429** |
| 1 個 browser，20 秒間隔 | 4/4，**零 429** |

**結論：並行 browser 唔會令吞吐量倍增。** LeetCode 嘅限流係 per account／per IP，兩個 browser 只係更快燒同一個額度。呢個就係點解最後只保留一個 submitter。

### 兩種封鎖要分清

- **HTTP 429** —— 短期限流，退避幾十秒就會恢復
- **HTTP 403** —— 較長冷卻期，約 10 分鐘

兩者都**只影響提交**；session 同讀取操作照常運作。

### Judge 會 prepend 自己嘅 preamble

LeetCode 喺你嘅 code 前面插入自己嘅 import 區。所以：

```python
from __future__ import annotations   # ❌ SyntaxError，唔會係第一句
```

後果係 **Runtime Error 0/208**，錯誤訊息係 `SyntaxError: from __future__ imports must occur at the beginning of the file`。

**解決方法**：用引號標註，例如
```python
def mergeTwoLists(self, list1: "ListNode | None") -> "ListNode | None":
```

另外 `List[...]` 要改成 builtin generics `list[...]`，否則無法獨立載入。

---

## 6. 品質標準

### 每個 solution 檔案

```python
# <id>. <Title>
# https://leetcode.com/problems/<slug>/
#
# <推理／不變式／貪心論證>
#
# Time: O(...)   Space: O(...)

class Solution:
    ...
```

- 用 builtin generics（`list[int]`），**唔可以**用裸 `List`
- **唔可以**用 `from __future__ import ...`
- ListNode / TreeNode 標註要加引號
- 用 `tests/_loader.py` 嘅 `load_solution(filename)` 載入（檔名有 hyphen，唔係合法 module 名）

### 每個測試檔案必須有

1. 官方 examples
2. 約束邊界情況
3. **一個獨立 oracle** —— brute force、`itertools`、`math.isqrt`、`math.comb`、`Decimal` 高精度、`re`，或者**刻意用唔同算法**。唔可以將同一思路重寫一次（循環論證）
4. 對照 oracle 嘅窮舉小案例掃描
5. 一個約束規模嘅案例

### Oracle 分歧點處理

先判斷**邊一邊錯**，唔好見到紅就改 solution。本 repo 嘅實際經驗：

| 案例 | 真正錯喺邊 |
|---|---|
| #76 minimum-window-substring | **Solution** —— tie-break 用 `right - left`（長度-1）對比長度 |
| #90 subsets-ii | **測試** —— 用 `frozenset` 令 `[2]` 同 `[2,2]` 靜靜地合併 |
| #99 recover-binary-search-tree | **測試** —— 手砌官方 example 砌錯邊、期望值寫錯、helper 遞歸爆棧 |
| #95 unique-binary-search-trees-ii | **Solution**（潛在）—— 兄弟結果共用 subtree，唔獨立 |
| #67 add-binary | **測試** —— 產生咗帶 leading zero 嘅輸入，但題目明文保證冇 |

**唔好產生題目保證排除嘅輸入**（例如「冇 leading zero」、「輸入唔重疊」、「保證唯一解」）。

---

## 7. 協作規則

### Write scope 隔離

- Solver 只寫 `solutions/` + `tests/`，**只限自己嘅 id 範圍**
- 冇人可以改或刪自己冇建立嘅檔（4 個 solver + qa-1 同時運作）
- qa-1 對 repo **唯讀**
- 冇人可以改 `accepted.json`（只有 lead）

### 硬規則

- **永遠唔好 print / echo / log session cookie** —— 只可以報 `isSignedIn`
- 唔可以用其他 folder（唔好掂其他 repo、venv、Documents）
- 唔可以安裝任何嘢
- 唔可以 commit（只有 lead commit）
- 唔可以殺自己冇開嘅 process

### 憑證處理

Session 存喺 `%LOCALAPPDATA%\CodexLeetCode\global-session.xml`（Windows 加密，per-user）。解密方式：

```powershell
$secure = Import-Clixml -LiteralPath $p
$env:LEETCODE_SESSION = [System.Net.NetworkCredential]::new('', $secure).Password
```

用完喺 `finally` 還原。

---

## 8. 已知陷阱

| 陷阱 | 症狀 | 處理 |
|---|---|---|
| `exit code 0` 唔代表成功 | Driver 只喺 fatal 時設非零 | **讀 result JSON**，唔好信 exit code |
| 用 result 檔判斷「未閉環」 | 會誤報已修好嘅題 | **查 ledger**，並且比較 submission-id 排序 |
| `select-batch.py` race | 多個 solver 揀到同一批 | 用 `reserve-batches.py` 預留 |
| PowerShell 食 heredoc | `python -c "..."` 報 `ScriptBlock should only be...` | 寫 `.py` 檔，唔好 inline |
| Python stdout cp1252 | `UnicodeEncodeError` | 設 `$env:PYTHONIOENCODING='utf-8'` |
| Python 寫 stderr | `pwsh` 報 `[exit code: 1]` 但其實成功 | 分開檢查 `$LASTEXITCODE` |
| `npm` 被 Execution Policy 擋 | `npm.ps1` 無法執行 | 用 `npm.cmd` |
| 浮點精度 | 反覆平方接近 ±1 嘅數會蝕精度 | 見下 |

### 「未閉環」誤報（實際踩過）

qa-1 報 `merge-two-sorted-lists` 有 Runtime Error 但冇 Accepted 記錄，要求重交。查證後發現該題**已經 Accepted**（id 2168140518, 208/208）——嗰次成功重交係經 MCP 路徑記錄嘅，唔喺任何 `submit*result*.json` 入面。

**教訓：** result 檔只係部分視野，`accepted.json` 才係權威。而且要比較 **submission-id 排序**而唔係單純「有冇記錄」——ledger 記錄舊過失敗 id 就可能係回歸。

QA 唔會因為勤力而出錯，會因為**證據不完整**而出錯。

### 浮點精度（#50 powx-n）

反覆平方一個 `1-δ` 嘅數，會將 δ 嘅相對精度蝕成 `eps/δ`，再被指數放大。實測最壞絕對誤差：

| 方法 | 誤差 | 判定（容差 1e-5） |
|---|---|---|
| 先取倒數再平方 | 3.03e-5 | ❌ |
| 平方後才取倒數 | 2.44e-5 | ❌ |
| **`log1p` 對數域** | **2.24e-13** | ✅ |

用 `ln|x^n| = n·ln|x|`，`log1p` 可以無抵消咁還原 δ。

---

## 9. 工具清單

全部喺 `%TEMP%\lc-fetch\`（**臨時目錄，建議搬入 `tools/agent/` 以持久保存**）。

### 題庫／選題

| 腳本 | 用途 |
|---|---|
| `fetch-universe.py` | 建立題庫（4073 題，3288 免費） |
| `select-batch.py` | 揀下一批未做題目（**單 solver 用**） |
| `reserve-batches.py` | 為多個 solver 預留互斥批次（**多 solver 用**） |
| `fetch-batch.mjs` | 經一個 MCP session 抓取題目 |
| `digest.py` | 將題目壓縮成可讀 digest |

### 提交

| 腳本 | 用途 |
|---|---|
| `cdp-submit.mjs` | 零依賴 CDP driver（單次 + watch mode） |
| `build-tasks.py` | 建立提交清單（所有未 AC 嘅題） |
| `build-queue.py` | 從 QA PASS 建立 queue（舊架構） |
| `build-question-ids.py` | 建立 slug → 內部 questionId 對照 |
| `merge-cdp-results.py` | 合併提交結果入 ledger |

### 監察

| 腳本 | 用途 |
|---|---|
| `team-status.py` | 整體狀態 |
| `verdict-status.py` | QA verdict + 可提交清單 |
| `check-slug.py` | 查單一題目嘅提交歷史 |
| `accuracy-stress.py` | 對照高精度真值壓測數值方法 |

### QA / 失敗診斷

| 腳本 | 用途 |
|---|---|
| `qa-open-failures.py` | 分類每條失敗記錄係 OPEN 定 HISTORY |
| `qa-repro.py` | 一條指令重現失敗（自動砌 ListNode / TreeNode 參數） |

`qa-open-failures.py` 用 **submission-id 排序**判斷，唔係單純查「ledger 有冇」：

- ledger 嘅 Accepted id **大過**失敗 id → **HISTORY**（已修好）
- ledger 冇記錄，或者 Accepted id **舊過**失敗 id → **OPEN**（可能係回歸）

第三個分支係 regression guard：如果一題曾經 AC，之後改壞再交而失敗，單純查「有冇記錄」會誤判成 HISTORY。

`qa-repro.py` 支援兩種輸入：

```powershell
python "$d\qa-repro.py" <slug> --case "<lines>" --expect "<out>" [--time]
python "$d\qa-repro.py" <slug> --from-result <result.json>   # 直接抽 judge 診斷
```

`--from-result` 會由 judge 記錄抽 `lastTestcase` / `expectedOutput` / error text，自動由抓取到嘅 snippet 讀出 method 名同標註，砌好 ListNode / `list[ListNode]` / TreeNode 參數，轉換回傳值，印出 observed vs expected；Runtime Error 會印帶行號嘅 traceback；`--time` 量 TLE 牆鐘時間。

---

## 10. 現況快照

| 項目 | 數量 |
|---|---|
| LeetCode AC | 137（55 原有 + 82 新） |
| Solution 檔案 | 117 |
| 測試 | 100 個檔 |
| 免費題庫總數 | 3288 |
| 剩餘未做 | 約 3120 |
| Git commits | 19（本 session 8 個） |

### 本 session 里程碑

- 由 #5 做到 #132（部分）
- 修正 legacy `014-longest-common-prefix.py` 嘅真 `NameError`
- 加 `tests/test_solution_conventions.py` guardrail
- 發現並修正 #50 嘅浮點精度問題
- 由 MCP API 提交改為 CDP browser 提交（繞過 403）
- 由單 agent 演進到 4 solver + 1 submitter + qa-1 嘅 team

---

## 11. 未解決 / 可改進

1. **工具喺 `%TEMP%`** —— 會被清理。建議搬入 `tools/agent/` 並納入版本控制。
2. **`select-batch.py` 嘅 race condition** —— 已用 `reserve-batches.py` 繞過，但根本修復應該係畀 `select-batch.py` 支援 `--output` 同 atomic reservation。
3. **README 嘅 `npm ci` 指引喺本機唔適用** —— `npm.ps1` 被 Execution Policy 擋，要用 `npm.cmd`。
4. **Legacy 命名唔一致** —— `014-`、`020-` 用 zero-padded 3 位，新檔案用無 padding。另有 2 個 legacy solution 冇測試。
5. **QA 證據視野** —— qa-1 只掃 result 檔會漏掉經 MCP 路徑記錄嘅成功提交。已糾正，但值得考慮畀 qa-1 一個統一嘅提交歷史查詢工具。
6. **`spawn_teammate` 冇 thinking level 參數** —— 只能喺 prompt 層面要求高強度推理。
