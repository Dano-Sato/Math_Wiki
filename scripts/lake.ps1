# Forward arguments to Lake using the repository-local toolchain.
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lean_env.ps1')
$leanLake = Join-Path $env:ELAN_HOME 'bin/lake.exe'
if (-not (Test-Path -LiteralPath $leanLake)) {
    throw 'Run powershell -ExecutionPolicy Bypass -File scripts/setup_lean.ps1 first.'
}
Push-Location $leanProjectRoot
try {
    & $leanLake @args
    $leanLakeExitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $leanLakeExitCode
