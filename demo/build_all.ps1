# ============================================================
#  build_all.ps1 - one-shot rebuild of the deployment package.
#
#  Steps:
#    1. npm run build        (regenerates demo/presentation/dist/)
#    2. python build_package (assembles dist-package/sudoku_demo/)
#    3. Compress-Archive     (produces dist-package/sudoku_demo.zip)
#
#  Run from any cwd:
#      .\demo\build_all.ps1
#  Or right-click in Explorer -> "Run with PowerShell".
#
#  Options:
#      -SkipNpm     reuse existing demo/presentation/dist (no Vite rebuild)
#      -SkipZip     stop after assembling the folder, don't zip
# ============================================================

[CmdletBinding()]
param(
    [switch]$SkipNpm,
    [switch]$SkipZip
)

$ErrorActionPreference = 'Stop'

# 用右鍵 "用 PowerShell 執行" / 雙擊時，腳本一拋錯視窗就瞬間關閉（看起來像閃退）。
# 這個 trap 攔下任何終止性錯誤，先把訊息留在畫面上、等使用者按 Enter 才關。
trap {
    Write-Host ''
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host ''
    Read-Host 'Build failed. Press Enter to close'
    exit 1
}

# Resolve repo root from this script's location (demo/build_all.ps1 -> ..)
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$PresDir  = Join-Path $RepoRoot 'demo\presentation'
$PkgDir   = Join-Path $RepoRoot 'dist-package\sudoku_demo'
$ZipPath  = Join-Path $RepoRoot 'dist-package\sudoku_demo.zip'

Write-Host ''
Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '  Sudoku Demo - build_all' -ForegroundColor Cyan
Write-Host '============================================================' -ForegroundColor Cyan
Write-Host "  Repo root : $RepoRoot"
Write-Host ''

# ── 1. npm run build ─────────────────────────────────────────────────────────
if ($SkipNpm) {
    Write-Host '[1/3] Skipping npm build (--SkipNpm)' -ForegroundColor Yellow
} else {
    Write-Host '[1/3] Building presentation dist (vite)...' -ForegroundColor Cyan
    Push-Location $PresDir
    try {
        & npm run build
        if ($LASTEXITCODE -ne 0) { throw "npm run build failed with exit $LASTEXITCODE" }
    } finally {
        Pop-Location
    }
    Write-Host '       OK.' -ForegroundColor Green
}
Write-Host ''

# ── 2. python demo/build_package.py ──────────────────────────────────────────
Write-Host '[2/3] Assembling dist-package/sudoku_demo/...' -ForegroundColor Cyan
Push-Location $RepoRoot
try {
    & python (Join-Path 'demo' 'build_package.py')
    if ($LASTEXITCODE -ne 0) { throw "build_package.py failed with exit $LASTEXITCODE" }
} finally {
    Pop-Location
}
Write-Host ''

# ── 3. Compress-Archive ──────────────────────────────────────────────────────
if ($SkipZip) {
    Write-Host '[3/3] Skipping zip (--SkipZip)' -ForegroundColor Yellow
} else {
    Write-Host '[3/3] Compressing -> sudoku_demo.zip ...' -ForegroundColor Cyan
    if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
    Compress-Archive -Path $PkgDir -DestinationPath $ZipPath -CompressionLevel Optimal
    $size = [Math]::Round((Get-Item $ZipPath).Length / 1MB, 1)
    Write-Host "       OK. ($size MB)" -ForegroundColor Green
}
Write-Host ''

# ── Sanity check: launcher.bat + SETUP.bat inside the zip are ASCII-only and
#    use the pyvenv.cfg check (catches future regressions of the two known bugs)
if (-not $SkipZip) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        foreach ($name in 'launcher.bat','SETUP.bat') {
            $entry = $archive.Entries | Where-Object { $_.FullName -like "*$name" } | Select-Object -First 1
            if (-not $entry) { throw "$name not found in zip" }
            $reader = New-Object System.IO.StreamReader($entry.Open())
            $content = $reader.ReadToEnd()
            $reader.Close()
            $nonAscii = ($content.ToCharArray() | Where-Object { [int]$_ -gt 127 }).Count
            $hasPyVenvCheck = $content -match 'pyvenv\.cfg'
            $ok = ($nonAscii -eq 0) -and $hasPyVenvCheck
            $color = if ($ok) { 'Green' } else { 'Red' }
            Write-Host ("  check {0,-14} non-ASCII={1}  pyvenv.cfg-check={2}" -f $name, $nonAscii, $hasPyVenvCheck) -ForegroundColor $color
            if (-not $ok) { throw "Regression detected in $name" }
        }
    } finally {
        $archive.Dispose()
    }
    Write-Host ''
}

Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '  DONE.' -ForegroundColor Cyan
if (-not $SkipZip) {
    Write-Host "  Upload to Drive: $ZipPath" -ForegroundColor Cyan
}
Write-Host '============================================================' -ForegroundColor Cyan
Write-Host ''
