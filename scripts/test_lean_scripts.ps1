# Offline integration tests: run the real wrappers in a disposable project with fake tools.
$ErrorActionPreference = 'Stop'
$testTemp = [IO.Path]::GetTempPath()
$testRoot = Join-Path $testTemp ('math-wiki-lean-test-' + [Guid]::NewGuid().ToString('N'))
$testOriginalLocation = Get-Location
$testEnvironment = @{}
foreach ($name in @('ELAN_HOME', 'MATHLIB_CACHE_DIR', 'PATH', 'MATHLIB_NO_CACHE_ON_UPDATE', 'GIT_CONFIG_COUNT')) {
    $testEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}
$testOriginalGitCount = 0
if ($env:GIT_CONFIG_COUNT) { $testOriginalGitCount = [int]$env:GIT_CONFIG_COUNT }
$global:leanTestCalls = [Collections.Generic.List[string]]::new()
$global:leanTestFailure = ''
$global:leanTestNextRevision = ''
$global:leanTestRoot = $testRoot

function Set-TestManifest([string]$Revision) {
    @{ packagesDir = '.lake/packages'; packages = @(@{ name = 'mathlib'; rev = $Revision; subDir = $null }) } |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $global:leanTestRoot 'lake-manifest.json')
}
function Assert-Test([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "Assertion failed: $Message" }
}
function Invoke-TestLake([string[]]$Arguments) {
    $global:leanTestCalls.Clear()
    & (Join-Path $testRoot 'scripts/lake.ps1') @Arguments
}
function Assert-TestCalls([string[]]$Expected) {
    Assert-Test (($global:leanTestCalls -join '|') -eq ($Expected -join '|')) "Expected $($Expected -join '|'), got $($global:leanTestCalls -join '|')"
}

try {
    New-Item -ItemType Directory -Path (Join-Path $testRoot 'scripts'), (Join-Path $testRoot '.tools/elan/bin') -Force | Out-Null
    foreach ($script in @('lean_env.ps1', 'mathlib_cache.ps1', 'setup_lean.ps1', 'lake.ps1')) {
        Copy-Item -LiteralPath (Join-Path $PSScriptRoot $script) -Destination (Join-Path $testRoot 'scripts')
    }
    Set-Content -LiteralPath (Join-Path $testRoot 'lean-toolchain') -Value 'leanprover/lean4:test-one'
    Set-TestManifest 'revision-one'
    $testLake = Join-Path $testRoot '.tools/elan/bin/lake.exe'
    $testElan = Join-Path $testRoot '.tools/elan/bin/elan.exe'
    New-Item -ItemType File -Path $testLake, $testElan | Out-Null
    Set-Item -Path "Function:$testLake" -Value {
        $call = $args -join ' '
        $global:leanTestCalls.Add($call)
        $global:LASTEXITCODE = 0
        if ($call -eq $global:leanTestFailure) { $global:LASTEXITCODE = 23; return }
        if ($call -eq 'update') {
            $revision = 'revision-one'
            if ($global:leanTestNextRevision) { $revision = $global:leanTestNextRevision }
            Set-TestManifest $revision
        }
        if ($call -eq 'exe cache get') {
            Assert-Test ($env:MATHLIB_NO_CACHE_ON_UPDATE -eq '1') 'post_update cache hook must be suppressed'
            $outputDir = Join-Path $global:leanTestRoot '.lake/packages/mathlib/.lake/build/lib/lean'
            New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
            Set-Content -LiteralPath (Join-Path $outputDir 'Mathlib.olean') -Value 'fake cache'
        }
    }
    Set-Item -Path "Function:$testElan" -Value { $global:LASTEXITCODE = 0 }
    $env:MATHLIB_NO_CACHE_ON_UPDATE = 'original'
    $marker = Join-Path $testRoot '.lake/mathlib-cache.key'
    $rootOLean = Join-Path $testRoot '.lake/packages/mathlib/.lake/build/lib/lean/Mathlib.olean'

    Invoke-TestLake @('build')
    Assert-TestCalls @('env lean --version', 'exe cache get', 'build')
    Assert-Test (Test-Path -LiteralPath $marker) 'first build writes marker'
    Assert-Test ($env:MATHLIB_NO_CACHE_ON_UPDATE -eq 'original') 'environment restored'
    Assert-Test ((Get-Location).Path -eq $testOriginalLocation.Path) 'working directory restored'
    Invoke-TestLake @('build')
    Assert-TestCalls @('build')

    Set-TestManifest 'revision-two'
    Invoke-TestLake @('-v', 'build', 'MathWiki')
    Assert-TestCalls @('env lean --version', 'exe cache get', '-v build MathWiki')
    Set-Content -LiteralPath (Join-Path $testRoot 'lean-toolchain') -Value 'leanprover/lean4:test-two'
    Invoke-TestLake @('env', 'lean', 'file with spaces.lean')
    Assert-TestCalls @('env lean --version', 'exe cache get', 'env lean file with spaces.lean')

    Remove-Item -LiteralPath $rootOLean
    $global:leanTestFailure = 'exe cache get'
    $failed = $false
    try { Invoke-TestLake @('build') } catch { $failed = $true }
    Assert-Test $failed 'cache failure aborts build'
    Assert-TestCalls @('env lean --version', 'exe cache get')
    Assert-Test (-not (Test-Path -LiteralPath $marker)) 'failed refresh invalidates old marker'
    Assert-Test ($env:MATHLIB_NO_CACHE_ON_UPDATE -eq 'original') 'environment restored on failure'
    $global:leanTestFailure = ''
    Invoke-TestLake @('build')
    Assert-TestCalls @('env lean --version', 'exe cache get', 'build')

    Set-TestManifest 'restore-failure'
    $global:leanTestFailure = 'env lean --version'
    $failed = $false
    try { Invoke-TestLake @('build') } catch { $failed = $true }
    Assert-Test $failed 'dependency restoration failure aborts build'
    Assert-TestCalls @('env lean --version')
    Assert-Test (-not (Test-Path -LiteralPath $marker)) 'restoration failure does not write marker'
    $global:leanTestFailure = ''

    Remove-Item -LiteralPath (Join-Path $testRoot 'lake-manifest.json')
    Invoke-TestLake @('build')
    Assert-TestCalls @('update', 'exe cache get', 'build')
    $global:leanTestNextRevision = 'revision-three'
    Invoke-TestLake @('update')
    Assert-TestCalls @('update', 'env lean --version', 'exe cache get')
    Invoke-TestLake @('update')
    Assert-TestCalls @('update')
    $global:leanTestFailure = 'update'
    Invoke-TestLake @('update')
    Assert-Test ($LASTEXITCODE -eq 23) 'update exit code is preserved'
    Assert-TestCalls @('update')
    $global:leanTestFailure = 'build'
    Invoke-TestLake @('build')
    Assert-Test ($LASTEXITCODE -eq 23) 'build exit code is preserved'
    $global:leanTestFailure = ''

    # Cache is absent here: help, cleanup and explicit/advanced invocations must still pass through.
    Remove-Item -LiteralPath $marker
    foreach ($arguments in @(@('build', '--help'), @('--version'), @('--no-cache', 'build'),
        @('--dir', 'other project', 'build'), @('-Kenv=dev', 'build'), @('--update', 'build'),
        @('exe', 'cache', 'get', 'Mathlib.Data.Finset.Card'), @('clean'))) {
        Invoke-TestLake $arguments
        Assert-TestCalls @(($arguments -join ' '))
    }

    $global:leanTestCalls.Clear()
    & (Join-Path $testRoot 'scripts/setup_lean.ps1')
    Assert-TestCalls @('env lean --version', 'exe cache get', 'build')
    $global:leanTestCalls.Clear()
    & (Join-Path $testRoot 'scripts/setup_lean.ps1')
    Assert-TestCalls @('build')
    Write-Host 'All Lean script integration tests passed.'
} finally {
    Set-Location $testOriginalLocation
    foreach ($name in $testEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($name, $testEnvironment[$name], 'Process')
    }
    [Environment]::SetEnvironmentVariable("GIT_CONFIG_KEY_$testOriginalGitCount", $null, 'Process')
    [Environment]::SetEnvironmentVariable("GIT_CONFIG_VALUE_$testOriginalGitCount", $null, 'Process')
    Remove-Item -Path "Function:$testLake", "Function:$testElan" -ErrorAction SilentlyContinue
    $resolvedTestRoot = [IO.Path]::GetFullPath($testRoot)
    if (-not $resolvedTestRoot.StartsWith([IO.Path]::GetFullPath($testTemp), [StringComparison]::OrdinalIgnoreCase) -or
        (Split-Path -Leaf $resolvedTestRoot) -notlike 'math-wiki-lean-test-*') { throw 'Unsafe test cleanup path.' }
    if (Test-Path -LiteralPath $resolvedTestRoot) { Remove-Item -LiteralPath $resolvedTestRoot -Recurse -Force }
    Remove-Variable -Name leanTestCalls, leanTestFailure, leanTestNextRevision, leanTestRoot -Scope Global -ErrorAction SilentlyContinue
}
