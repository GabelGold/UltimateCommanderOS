#Requires -Version 5.1
# Ultimate Commander OS - einmal ausfuehren: kopieren, reparieren, bauen, dokumentieren.
# Christian Schmitt, Solingen - 13. August 2026
[CmdletBinding()]
param(
    [string]$Source = "I:\Ultimate Commander OS",
    [string]$Dest   = "G:\Ultimate Commander OS",
    [switch]$SkipBuild,
    [switch]$SkipGit,
    [switch]$SkipExplorer
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$script:Started = Get-Date
$script:Log = New-Object System.Collections.Generic.List[string]

function Write-Step {
    param([string]$Message, [string]$Color = "Cyan")
    $line = "[{0:HH:mm:ss}] {1}" -f (Get-Date), $Message
    $script:Log.Add($line) | Out-Null
    Write-Host $line -ForegroundColor $Color
}

function Get-Py {
    $cmd = Get-Command py -ErrorAction SilentlyContinue
    if ($cmd) { return @($cmd.Source, "-3.12") }
    $p312 = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
    if (Test-Path $p312) { return @($p312) }
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py) { return @($py.Source) }
    throw "Python 3.12 nicht gefunden. Bitte python.org 3.12 installieren."
}

function Invoke-Robo {
    param([string]$From, [string]$To)
    New-Item -ItemType Directory -Force -Path $To | Out-Null
    $robo = @(
        $From, $To, "/E", "/MT:16", "/R:1", "/W:1",
        "/NFL", "/NDL", "/NJH", "/NJS", "/NP",
        "/XD", "venv", ".venv", "dist", "build", "__pycache__", ".git", "cache", "logs",
        "/XF", "*.log", "*.iso"
    )
    & robocopy @robo | Out-Null
    $code = $LASTEXITCODE
    if ($code -ge 8) { throw "robocopy failed with code $code ($From -> $To)" }
    return $code
}

function Repair-Tree {
    param([string]$Root)
    Write-Step "Reparatur in $Root"
    $req = Join-Path $Root "requirements.txt"
    if (Test-Path $req) {
        $text = Get-Content -Raw -LiteralPath $req
        $pkgLines = $text -split "`r?`n" | Where-Object { $_ -and ($_ -notmatch '^\s*#') }
        $hasNetifacesPkg = $pkgLines | Where-Object { $_ -match '^\s*netifaces' }
        if ($hasNetifacesPkg) {
            $text = $text -replace "(?m)^\s*netifaces[^\r\n]*", "ifaddr>=0.2.0"
            if ($text -notmatch "(?m)^\s*ifaddr") { $text += "`nifaddr>=0.2.0`n" }
            [System.IO.File]::WriteAllText($req, $text)
            Write-Step "netifaces -> ifaddr" "Yellow"
        }
    }
    foreach ($rel in @("src", "src\backend", "src\ui", "tests")) {
        $dir = Join-Path $Root $rel
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        $init = Join-Path $dir "__init__.py"
        if (-not (Test-Path $init)) {
            [System.IO.File]::WriteAllText($init, "# package marker`n")
        }
    }
    $dash = Join-Path $Root "src\backend\Dashboard.py"
    $legacy = Join-Path $Root "src\backend\dashboard.py"
    if ((Test-Path $legacy) -and -not (Test-Path $dash)) {
        Copy-Item $legacy $dash -Force
    }
    Get-ChildItem -LiteralPath $Root -Recurse -Filter "*.py" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "\\venv\\|\\dist\\|\\build\\" } |
        ForEach-Object {
            $raw = Get-Content -Raw -LiteralPath $_.FullName -ErrorAction SilentlyContinue
            if ($null -eq $raw) { return }
            if ($raw -match "import netifaces" -or $raw -match "from netifaces") {
                $fixed = $raw.Replace("import netifaces", "import ifaddr")
                Set-Content -LiteralPath $_.FullName -Value $fixed -Encoding UTF8
                Write-Step ("import-fix " + $_.Name) "Yellow"
            }
        }
}

Write-Host ""
Write-Host "  ULTIMATE COMMANDER OS  -  GODMODE DEPLOY" -ForegroundColor Green
Write-Host "  Christian Schmitt, Solingen  -  13. August 2026" -ForegroundColor DarkGreen
Write-Host ""

if (-not (Test-Path "G:\")) { throw "Laufwerk G: ist nicht bereit." }
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

$selfDest = Join-Path $Dest "GODMODE_DEPLOY.ps1"
if ($PSCommandPath -and (Test-Path $PSCommandPath) -and ($PSCommandPath -ne $selfDest)) {
    Copy-Item -LiteralPath $PSCommandPath -Destination $selfDest -Force
}

$srcEntry = Join-Path $Source "ultimate_commander.py"
$dstEntry = Join-Path $Dest "ultimate_commander.py"
if (-not (Test-Path $srcEntry) -and (Test-Path $dstEntry)) {
    Write-Step "Quelle fehlt - seede I: aus G: (ohne venv/dist)"
    if (Test-Path "I:\") {
        [void](Invoke-Robo -From $Dest -To $Source)
    } else {
        Write-Step "I: nicht bereit - arbeite nur auf G:" "Yellow"
    }
}

if (Test-Path $srcEntry) {
    Write-Step "robocopy /MT:16  $Source  ->  $Dest"
    [void](Invoke-Robo -From $Source -To $Dest)
} else {
    Write-Step "Kein Quellbaum auf I: - verwende vorhandenen Zielbaum" "Yellow"
}

Repair-Tree -Root $Dest
Set-Location -LiteralPath $Dest

$pyArgs = @(Get-Py)
$venvPy = Join-Path $Dest "venv\Scripts\python.exe"
Write-Step ("venv + pip (" + ($pyArgs -join " ") + ")")
if (-not (Test-Path $venvPy)) {
    if ($pyArgs.Count -ge 2) {
        & $pyArgs[0] $pyArgs[1] -m venv (Join-Path $Dest "venv")
    } else {
        & $pyArgs[0] -m venv (Join-Path $Dest "venv")
    }
}
if (-not (Test-Path $venvPy)) { throw "venv python fehlt: $venvPy" }

& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r (Join-Path $Dest "requirements-dev.txt")

Write-Step "ENCRYPTION_KEY"
& $venvPy -c "from src.backend.security import ensure_encryption_key; print(ensure_encryption_key()[:8])"

Write-Step "live_check --once + pytest"
& $venvPy (Join-Path $Dest "live_check.py") --once
$liveCode = $LASTEXITCODE
& $venvPy -m pytest (Join-Path $Dest "tests") -v
$testCode = $LASTEXITCODE
$okColor = "Yellow"
if (($liveCode -eq 0) -and ($testCode -eq 0)) { $okColor = "Green" }
Write-Step "live_check exit=$liveCode  pytest exit=$testCode" $okColor

if (-not $SkipBuild) {
    Write-Step "PyInstaller (windowed, no console)"
    $spec = Join-Path $Dest "installer\UltimateCommander.spec"
    & $venvPy -m PyInstaller --noconfirm $spec
    $exe = Join-Path $Dest "dist\UltimateCommanderOS\UltimateCommanderOS.exe"
    if (Test-Path $exe) {
        Write-Step "EXE ok: $exe" "Green"
    } else {
        Write-Step "EXE fehlt nach PyInstaller" "Red"
    }

    $isccCandidates = @(
        (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
        (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe")
    )
    $iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($iscc) {
        Write-Step "Inno Setup $iscc"
        & $iscc (Join-Path $Dest "installer\UltimateInstaller.iss")
    } else {
        Write-Step "ISCC nicht installiert - UltimateInstaller.iss liegt bereit" "Yellow"
    }
}

if (-not $SkipGit) {
    Write-Step "git init / commit / push"
    git config --global --add safe.directory $Dest
    if (-not (Test-Path (Join-Path $Dest ".git"))) {
        git -C $Dest init -b main | Out-Null
    }
    git -C $Dest config user.name  "Christian Schmitt"
    git -C $Dest config user.email "christian.schmitt@users.noreply.github.com"
    git -C $Dest remote remove origin 2>$null
    git -C $Dest remote add origin "https://github.com/GabelGold/UltimateCommanderOS.git"
    git -C $Dest add -A
    git -C $Dest status --short
    git -C $Dest commit -m "chore: Ultimate Commander OS 1.0.0 production tree"
    git -C $Dest push -u origin main
}

Write-Step "Dokumente + SHA-256"
$logFile = Join-Path $env:TEMP "ucos_deploy.log"
$script:Log -join "`r`n" | Set-Content -LiteralPath $logFile -Encoding UTF8
& $venvPy (Join-Path $Dest "tools\write_docs.py") $Dest $Source $script:Started.ToString("s") $logFile

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host (" FERTIG  " + $Dest) -ForegroundColor Green
Write-Host (" Start   " + (Join-Path $Dest "start.bat")) -ForegroundColor Green
Write-Host (" EXE     " + (Join-Path $Dest "dist\UltimateCommanderOS\UltimateCommanderOS.exe")) -ForegroundColor Green
Write-Host " Repo    https://github.com/GabelGold/UltimateCommanderOS" -ForegroundColor Green
Write-Host (" Check   " + (Join-Path $Dest "MASTER_CONTROL.txt")) -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

if (-not $SkipExplorer) {
    Start-Process explorer.exe $Dest
}
exit 0
