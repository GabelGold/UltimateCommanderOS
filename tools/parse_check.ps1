$errs = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile(
    (Join-Path $PSScriptRoot "..\GODMODE_DEPLOY.ps1"),
    [ref]$null,
    [ref]$errs
)
if ($errs -and $errs.Count) {
    $errs | ForEach-Object { $_.ToString() }
    exit 1
}
Write-Output "PARSE_OK"
exit 0
