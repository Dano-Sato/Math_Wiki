# Shared by setup_lean.ps1 and lake.ps1; dot-source after lean_env.ps1.
function Get-MathlibCacheState {
    $manifestPath = Join-Path $leanProjectRoot 'lake-manifest.json'
    if (-not (Test-Path -LiteralPath $manifestPath)) { return $null }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $mathlib = @($manifest.packages | Where-Object { $_.name -eq 'mathlib' })
    if ($mathlib.Count -ne 1) { throw 'Expected one Mathlib dependency in lake-manifest.json.' }
    $packageDir = Join-Path (Join-Path $leanProjectRoot $manifest.packagesDir) 'mathlib'
    if ($mathlib[0].subDir) { $packageDir = Join-Path $packageDir $mathlib[0].subDir }
    $manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash
    $toolchainHash = (Get-FileHash -LiteralPath (Join-Path $leanProjectRoot 'lean-toolchain') -Algorithm SHA256).Hash
    [PSCustomObject]@{
        Key = "v1:$toolchainHash`:$manifestHash"
        # The full cache includes this root module. Also detect a removed package/build tree.
        RootOLean = Join-Path $packageDir '.lake/build/lib/lean/Mathlib.olean'
    }
}

function Initialize-MathlibCache {
    param([Parameter(Mandatory = $true)][string]$Lake)

    $marker = Join-Path $leanProjectRoot '.lake/mathlib-cache.key'
    $state = Get-MathlibCacheState
    if ($state -and (Test-Path -LiteralPath $marker) -and
        (Test-Path -LiteralPath $state.RootOLean) -and
        (Get-Content -LiteralPath $marker -Raw).Trim() -eq $state.Key) {
        return
    }

    if (Test-Path -LiteralPath $marker) { Remove-Item -LiteralPath $marker }
    # Own the download so Mathlib's post_update hook does not fetch it a second time.
    $previousNoCache = $env:MATHLIB_NO_CACHE_ON_UPDATE
    $env:MATHLIB_NO_CACHE_ON_UPDATE = '1'
    Push-Location $leanProjectRoot
    try {
        if ($state) {
            # Restore the exact manifest revisions, without updating the lock file.
            & $Lake env lean --version
            if ($LASTEXITCODE -ne 0) { throw 'Restoring locked Lake dependencies failed.' }
        } else {
            & $Lake update
            if ($LASTEXITCODE -ne 0) { throw 'Resolving Lake dependencies failed.' }
        }
        Write-Host 'Fetching the Mathlib precompiled cache (first use or changed dependencies/toolchain)...'
        & $Lake exe cache get
        if ($LASTEXITCODE -ne 0) {
            throw 'Downloading the Mathlib cache failed. Retry setup_lean.ps1 or lake.ps1 build; the library build was not started.'
        }
        $state = Get-MathlibCacheState
        if (-not $state -or -not (Test-Path -LiteralPath $state.RootOLean)) {
            throw 'The Mathlib cache is incomplete (Mathlib.olean is missing). Retry lake.ps1 exe cache get before building.'
        }
        # Write only after success. Failed/interrupted downloads are retried on the next build.
        Set-Content -LiteralPath $marker -Value $state.Key -Encoding ASCII
    } finally {
        $env:MATHLIB_NO_CACHE_ON_UPDATE = $previousNoCache
        Pop-Location
    }
}

function Get-MathlibCacheCommand {
    param([object[]]$LakeArguments)

    # Advanced workspace/config overrides retain Lake's own behavior. Do not fetch
    # this repository's cache for another project, a help request, or --no-cache.
    $command = ''
    foreach ($argument in $LakeArguments) {
        if ($argument -in @('--help', '-h', '--version', '--no-cache', '--update')) {
            return ''
        }
        if (-not $command) {
            if ($argument -cmatch '^(--(dir|file|packages)(=|$)|-[dfK])') { return '' }
            if (-not $argument.StartsWith('-')) { $command = [string]$argument }
        }
    }
    return $command
}
