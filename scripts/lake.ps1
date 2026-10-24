# Forward arguments to Lake using the repository-local toolchain.
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'lean_env.ps1')
. (Join-Path $PSScriptRoot 'mathlib_cache.ps1')
$leanLake = Join-Path $env:ELAN_HOME 'bin/lake.exe'
if (-not (Test-Path -LiteralPath $leanLake)) {
    throw 'Run powershell -ExecutionPolicy Bypass -File scripts/setup_lean.ps1 first.'
}
Push-Location $leanProjectRoot
$leanPreviousNoCache = $env:MATHLIB_NO_CACHE_ON_UPDATE
try {
    $leanCacheCommand = Get-MathlibCacheCommand -LakeArguments $args
    if ($leanCacheCommand -in @('build', 'env', 'lean', 'test', 'lint', 'serve')) {
        Initialize-MathlibCache -Lake $leanLake
    }
    if ($leanCacheCommand -eq 'update') {
        $env:MATHLIB_NO_CACHE_ON_UPDATE = '1'
    }
    & $leanLake @args
    $leanLakeExitCode = $LASTEXITCODE
    if ($leanCacheCommand -eq 'update' -and $leanLakeExitCode -eq 0) {
        Initialize-MathlibCache -Lake $leanLake
    }
} finally {
    $env:MATHLIB_NO_CACHE_ON_UPDATE = $leanPreviousNoCache
    Pop-Location
}
exit $leanLakeExitCode
