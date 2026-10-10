$ErrorActionPreference = 'Stop'
Write-Host 'Log in to https://leetcode.com in your browser.'
Write-Host 'Open F12 > Application (or Storage) > Cookies > https://leetcode.com.'
Write-Host 'Copy the value of LEETCODE_SESSION. Paste only into the hidden prompt below.'
$taskSecureSession = Read-Host 'LEETCODE_SESSION (hidden)' -AsSecureString
if ($taskSecureSession.Length -eq 0) { throw 'No session entered; nothing was saved.' }
$taskSessionDir = Join-Path $env:LOCALAPPDATA 'CodexLeetCode'
New-Item -ItemType Directory -Path $taskSessionDir -Force | Out-Null
$taskSecureSession | Export-Clixml -LiteralPath (Join-Path $taskSessionDir 'global-session.xml')
Write-Host 'Saved with Windows encryption for your Windows user. Checking the connection...'
& (Join-Path $PSScriptRoot 'start.ps1') -Check
exit $LASTEXITCODE
