# Dot-source this file to use this repository's Lean installation in the current shell.
$leanProjectRoot = Split-Path -Parent $PSScriptRoot
$env:ELAN_HOME = Join-Path $leanProjectRoot '.tools/elan'
$env:MATHLIB_CACHE_DIR = Join-Path $leanProjectRoot '.tools/mathlib-cache'
$leanBin = Join-Path $env:ELAN_HOME 'bin'
if (($env:PATH -split ';') -notcontains $leanBin) {
    $env:PATH = "$leanBin;$env:PATH"
}
# Git for Windows should verify HTTPS against the Windows certificate store.
# Use process-only config so Lake's child Git processes inherit it.
$leanGitConfigCount = 0
if ($env:GIT_CONFIG_COUNT) { $leanGitConfigCount = [int]$env:GIT_CONFIG_COUNT }
$leanHasSchannel = $false
for ($leanGitIndex = 0; $leanGitIndex -lt $leanGitConfigCount; $leanGitIndex++) {
    if ([Environment]::GetEnvironmentVariable("GIT_CONFIG_KEY_$leanGitIndex", 'Process') -eq 'http.sslBackend' -and
        [Environment]::GetEnvironmentVariable("GIT_CONFIG_VALUE_$leanGitIndex", 'Process') -eq 'schannel') {
        $leanHasSchannel = $true
    }
}
if (-not $leanHasSchannel) {
    [Environment]::SetEnvironmentVariable("GIT_CONFIG_KEY_$leanGitConfigCount", 'http.sslBackend', 'Process')
    [Environment]::SetEnvironmentVariable("GIT_CONFIG_VALUE_$leanGitConfigCount", 'schannel', 'Process')
    $env:GIT_CONFIG_COUNT = [string]($leanGitConfigCount + 1)
}
