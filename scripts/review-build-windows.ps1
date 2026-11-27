<#
.SYNOPSIS
  Compile and inspect the Windows minimal-security launcher in a disposable VM.
.DESCRIPTION
  Does not run Discord, inject a DLL, or install anything into Discord.
  Only use with source that you have independently reviewed.
#>
[CmdletBinding()]
param([switch]$SkipDefenderScan)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $Root

try {
    if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
        throw "Rust Cargo is missing. Install a trusted Rust toolchain first."
    }

    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 scripts/check-windows-minimal.py
        if ($LASTEXITCODE -ne 0) { throw "Static security checks failed." }
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python scripts/check-windows-minimal.py
        if ($LASTEXITCODE -ne 0) { throw "Static security checks failed." }
    } else {
        throw "Python 3 is required for the static security checks."
    }

    # Force the same target profile as the Windows CI job.
    $env:RUSTFLAGS = "-C target-feature=+crt-static"
    & cargo +stable-x86_64-pc-windows-msvc test --locked -p phoenix-inject
    if ($LASTEXITCODE -ne 0) { throw "Rust unit tests failed." }

    & cargo +stable-x86_64-pc-windows-msvc build --locked --release -p phoenix-loader -p phoenix-inject
    if ($LASTEXITCODE -ne 0) { throw "Windows build failed." }

    $dll = Join-Path $Root "target/release/phoenix.dll"
    $launcher = Join-Path $Root "target/release/phoenix-inject.exe"
    foreach ($file in @($dll, $launcher)) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            throw "Expected artifact missing: $file"
        }
    }

    $dllSha256 = (Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash.ToLowerInvariant()
    $launcherSha256 = (Get-FileHash -LiteralPath $launcher -Algorithm SHA256).Hash.ToLowerInvariant()
    $sidecar = "$dll.sha256"
    [System.IO.File]::WriteAllText($sidecar, $dllSha256, [System.Text.Encoding]::ASCII)

    Write-Host "DLL SHA-256: $dllSha256"
    Write-Host "Launcher SHA-256: $launcherSha256"
    Write-Host "Matching DLL sidecar: $sidecar"

    if (-not $SkipDefenderScan -and (Get-Command Start-MpScan -ErrorAction SilentlyContinue)) {
        Write-Host "Requesting Microsoft Defender scans of the two local binaries..."
        Start-MpScan -ScanType CustomScan -ScanPath $dll
        Start-MpScan -ScanType CustomScan -ScanPath $launcher
    } elseif (-not $SkipDefenderScan) {
        Write-Warning "Microsoft Defender PowerShell scan command not available. No antivirus scan performed."
    }

    Write-Warning "A successful build, matching hash, or clean antivirus scan does NOT prove the program is malware-free."
    Write-Warning "This script has NOT launched or verified Discord Phoenix functionality."
}
finally {
    Pop-Location
}
