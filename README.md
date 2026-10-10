# LeetCode Practice Solutions

This repository is my personal space to save and organize my practice code for LeetCode problems. The [solutions](solutions/) folder contains Python solutions and notebooks with explanations and visualizations for various coding challenges.

AI agents: read [AGENTS.md](AGENTS.md) for the problem-solving workflow, MCP/CLI commands, authentication handling, and judge-result verification.

## LeetCode MCP for Codex (Windows)

This workspace uses [jinzcdev/leetcode-mcp-server](https://github.com/jinzcdev/leetcode-mcp-server), pinned to 1.4.0, for **leetcode.com**. Node.js 20 or later is required. Dependencies are local to `tools/leetcode`; solutions are stored in `solutions/`.

Restore dependencies from the repository root:

```powershell
npm ci --prefix .\tools\leetcode --ignore-scripts --no-audit --no-fund
```

The local, Git-ignored `.codex/config.toml` configures the `leetcode` MCP server for this trusted project. On another checkout, configure a STDIO server that runs Windows PowerShell with `-NoProfile -ExecutionPolicy Bypass -File` and the absolute path to `tools/leetcode/start.ps1`. Restart Codex after adding the server or changing credentials to reload its tools.

Public problem descriptions and Daily Challenges work without login. To enable website testing and submission:

1. Log in to `https://leetcode.com` in your browser.
2. Open developer tools (F12), then **Application / Storage > Cookies > https://leetcode.com**.
3. Copy the **value** of `LEETCODE_SESSION`.
4. Run the following command and paste the value into its hidden local prompt. Do not paste it into chat or a source file.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\leetcode\login.ps1
```

The helper stores the session under `%LOCALAPPDATA%\CodexLeetCode\global-session.xml`, encrypted by Windows for the current Windows user. The launcher supplies it to the server through its process environment. The login check is read-only; it does not submit a solution. If the session expires, repeat the login command.

To check public access and, when configured, login status:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\leetcode\start.ps1 -Check
```

This verifies the MCP handshake, available tools, Two Sum, the live Daily Challenge, and authenticated status when credentials are present. It does not verify website code execution or submission. After restarting Codex, try: **"Get today's LeetCode Daily Challenge, explain it in Traditional Chinese, and write a Python solution in this repo."**
