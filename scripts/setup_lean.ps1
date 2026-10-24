# Install Lean locally, restore pinned dependencies, fetch needed cache, and build.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
. (Join-Path $PSScriptRoot 'lean_env.ps1')
. (Join-Path $PSScriptRoot 'mathlib_cache.ps1')
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required. Install Git for Windows before running this script.'
}

$leanElan = Join-Path $env:ELAN_HOME 'bin/elan.exe'
if (-not (Test-Path -LiteralPath $leanElan)) {
    $leanBootstrap = Join-Path $leanProjectRoot '.tools/bootstrap'
    New-Item -ItemType Directory -Path $leanBootstrap -Force | Out-Null
    $leanArchive = Join-Path $leanBootstrap 'elan-v4.2.4.zip'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://github.com/leanprover/elan/releases/download/v4.2.4/elan-x86_64-pc-windows-msvc.zip' -OutFile $leanArchive
    Expand-Archive -LiteralPath $leanArchive -DestinationPath $leanBootstrap -Force
    & (Join-Path $leanBootstrap 'elan-init.exe') -y --no-modify-path --default-toolchain none
    if ($LASTEXITCODE -ne 0) { throw 'Elan installation failed.' }
}

$leanLake = Join-Path $env:ELAN_HOME 'bin/lake.exe'
Push-Location $leanProjectRoot
try {
    & $leanElan toolchain install ((Get-Content -LiteralPath 'lean-toolchain' -Raw).Trim())
    if ($LASTEXITCODE -ne 0) { throw 'Lean toolchain installation failed.' }
    Initialize-MathlibCache -Lake $leanLake
    & $leanLake build
    if ($LASTEXITCODE -ne 0) { throw 'Lean library build failed.' }
} finally {
    Pop-Location
}
Write-Host 'Lean setup complete. Build with: .\scripts\lake.ps1 build'
