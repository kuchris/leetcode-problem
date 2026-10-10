# Agent instructions

## Scope and conventions

This repository contains personal LeetCode practice solutions for **leetcode.com**.
Use Python 3 unless the user requests another language. Explain solutions in
Traditional Chinese/Cantonese, keeping useful English algorithm terms.

Run commands from the repository root in PowerShell. Save new solutions as
`solutions/<questionFrontendId>-<titleSlug>.py`, with the problem URL, a LeetCode-compatible
`Solution` class, and brief reasoning and complexity comments. Use the displayed
problem number, not the internal `questionId`. Preserve existing solutions,
notebooks, and unrelated working-tree changes.

## Connect to LeetCode

Prefer the connected `leetcode` MCP tools when available. If the agent's tool
catalog lacks them, use the existing CLI bridge; it starts the same MCP server
and loads the same locally saved credentials:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\leetcode\start.ps1 -Check
node .\tools\leetcode\call.mjs get_user_status
node .\tools\leetcode\call.mjs get_daily_challenge
```

The connection check must report successful problem retrieval. Authenticated
operations additionally require `isSignedIn: true`; the direct `get_user_status`
response places this value under `status.isSignedIn`. Public retrieval can succeed
without a session, so a successful process exit alone does not prove login.

For missing dependencies, a new checkout, or expired credentials, follow
[README.md](README.md#leetcode-mcp-for-codex-windows). The launchers require Windows,
PowerShell, and Node.js; the saved session belongs to the Windows user who created
it. A different machine/user needs its own login. Reuse a working login.

Keep credentials in the launcher's local credential store. Never print or commit
cookies, decrypted sessions, or credential files, or ask the user to paste them
into chat. The user enters a replacement session through `login.ps1`'s hidden
local prompt. `.codex/config.toml` contains machine-specific paths and is ignored
by Git; other agents can use `call.mjs` without importing that Codex configuration.

## Solve a problem or Daily Challenge

1. Fetch the live problem. For Daily, call `get_daily_challenge` on every new task;
   read `date` and `problem.question` rather than reusing an earlier chat's problem.
   The user's timezone is Asia/Tokyo. If the returned challenge date differs from
   the user's local date, state the actual returned date. For a specified problem,
   call `get_problem` with `titleSlug` and read `problem` in the response.
2. Read the statement, constraints, examples, and Python method signature before
   implementing. Explain the key invariant or greedy argument and define the
   variables used in the complexity analysis.
3. Validate official examples and relevant edge cases locally. For a nontrivial
   algorithm, use an independent brute-force oracle on small inputs where feasible
   and a constraint-sized case. Put reusable tests in `tests/`; run the relevant
   tests with `python -m unittest discover -s tests -v`.
4. When website testing is part of the request, call `run_code` with `lang: python3`
   and the exact saved source. Confirm `check.correct_answer` and the returned
   testcase counts, not just a successful CLI exit.
5. Submit when the user requests submission or completion of a Daily on LeetCode.
   Explanation-only or local-code requests do not require submission. Honor any
   explicit user limits and existing authorization without asking for it again.
   Use `submit_solution` with the same tested source, then inspect the final judge
   result. If a submission times out after receiving an ID, inspect that submission
   with `get_problem_submission_report` before considering another submission.
6. Report the problem number/title, source-file link, validation performed, and
   remaining limits. Claim Accepted only when the judge returns
   `check.status_msg == "Accepted"` with matching correct/total testcase counts.
   Include `https://leetcode.com/submissions/detail/<submission_id>/` when available.

## CLI arguments for website testing and submission

`call.mjs` accepts a tool name and an optional **UTF-8 JSON file without a BOM**.
Tool errors produce a nonzero exit, but a completed Wrong Answer or compilation
error can still exit zero; inspect the result JSON. Build JSON with serialization
so Python newlines and quotes are preserved. Use this template after replacing
the slug and source path with the fetched problem and actual local solution:

```powershell
$taskArgs = @{
    titleSlug = '<titleSlug>'
    lang = 'python3'
    typedCode = Get-Content -Raw -LiteralPath '.\solutions\<questionFrontendId>-<titleSlug>.py'
    timeoutMs = 60000
}
# For run_code, optionally add dataInput using the problem's exampleTestcases.
$taskJson = Join-Path ([System.IO.Path]::GetTempPath()) ('leetcode-' + [guid]::NewGuid().ToString() + '.json')
[System.IO.File]::WriteAllText($taskJson, ($taskArgs | ConvertTo-Json), [System.Text.UTF8Encoding]::new($false))
try {
    node .\tools\leetcode\call.mjs run_code $taskJson
    if ($LASTEXITCODE -ne 0) { throw 'LeetCode tool failed.' }
} finally {
    Remove-Item -LiteralPath $taskJson
}
```

For an authorized submission, use `submit_solution` instead of `run_code` after
testing passes. For other tools, use the same JSON-file mechanism with the tool's
own arguments (for example, `{ "titleSlug": "two-sum" }` for `get_problem`).
Read the installed tool schemas/source when parameters are unclear; the upstream
implementation is under `tools/leetcode/node_modules/@jinzcdev/leetcode-mcp-server/build/mcp/tools/`.
