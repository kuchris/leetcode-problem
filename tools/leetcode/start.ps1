param([switch]$Check)
$ErrorActionPreference = 'Stop'
$taskSessionPath = Join-Path $env:LOCALAPPDATA 'CodexLeetCode\global-session.xml'
$taskPreviousSession = $env:LEETCODE_SESSION
try {
    if (-not $env:LEETCODE_SESSION -and (Test-Path -LiteralPath $taskSessionPath)) {
        $taskSecureSession = Import-Clixml -LiteralPath $taskSessionPath
        $env:LEETCODE_SESSION = [System.Net.NetworkCredential]::new('', $taskSecureSession).Password
    }
    if ($Check) {
        & node (Join-Path $PSScriptRoot 'check.mjs')
    } else {
        & node (Join-Path $PSScriptRoot 'node_modules\@jinzcdev\leetcode-mcp-server\build\index.js') --site global --transport stdio
    }
    $taskExitCode = $LASTEXITCODE
} finally {
    $env:LEETCODE_SESSION = $taskPreviousSession
}
exit $taskExitCode
