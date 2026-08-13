# Placeholder: baut spaeter ein Boot-ISO aus dem Release-Ordner.
# Benoetigt Windows ADK / oscdimg.exe
[CmdletBinding()]
param(
    [string]$Source = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$OutIso = (Join-Path (Join-Path $PSScriptRoot "..") "dist\UltimateCommanderOS.iso"),
    [string]$Label = "UCOS_2026"
)

$ErrorActionPreference = "Stop"
$oscdimg = @(
    "${env:ProgramFiles(x86)}\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe",
    "${env:ProgramFiles}\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

Write-Host "ISO-Quelle : $Source"
Write-Host "ISO-Ziel   : $OutIso"
if (-not $oscdimg) {
    Write-Host "oscdimg.exe nicht gefunden. Windows ADK installieren, dann erneut ausfuehren."
    Write-Host "Beispiel: oscdimg -u2 -l$Label `"$Source`" `"$OutIso`""
    exit 2
}
New-Item -ItemType Directory -Force -Path (Split-Path $OutIso) | Out-Null
& $oscdimg -u2 -l$Label $Source $OutIso
if ($LASTEXITCODE -ne 0) { throw "oscdimg exit $LASTEXITCODE" }
Write-Host "ISO erstellt: $OutIso"
