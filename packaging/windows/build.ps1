$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
& (Join-Path $root "scripts\build.ps1") @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
