$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$packagingRoot = Join-Path $root ".packaging"
$buildId = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$staging = Join-Path $packagingRoot $buildId
& $python -m pip install --disable-pip-version-check --no-build-isolation --no-deps --editable $root
if ($LASTEXITCODE -ne 0) { throw "Installing the checked-out Lab source failed with exit code $LASTEXITCODE" }
& $python -m PyInstaller --noconfirm --clean --onedir --windowed --optimize 2 --log-level WARN `
  --name IPCommandMicLab --paths (Join-Path $root "src") `
  --collect-data ip_commandmic_lab `
  --hidden-import ip_commandmic.display --hidden-import ip_commandmic.test_app `
  --distpath (Join-Path $staging "dist") --workpath (Join-Path $staging "build") `
  --specpath $staging `
  (Join-Path $PSScriptRoot "entry.py")
if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }
$dist = Join-Path $staging "dist\IPCommandMicLab"
Copy-Item -LiteralPath (Join-Path $root "packaging\windows\IPCommandMicLab.exe.config") `
  -Destination $dist
function Test-PackagedStartup([string]$label) {
  $smoke = Start-Process -FilePath (Join-Path $dist "IPCommandMicLab.exe") `
    -ArgumentList "--package-smoke-test" -PassThru -WindowStyle Hidden
  if (-not $smoke.WaitForExit(15000)) {
    $smoke.Kill()
    throw "$label startup smoke test timed out"
  }
  if ($smoke.ExitCode -ne 0) { throw "$label startup smoke test failed with exit code $($smoke.ExitCode)" }
}
Test-PackagedStartup "Packaged"

# Windows applies Mark-of-the-Web to every file extracted from a downloaded
# ZIP. Reproduce that state so releases cannot pass CI while failing for users.
Get-ChildItem -LiteralPath $dist -Recurse -File -Filter "*.dll" | ForEach-Object {
  "[ZoneTransfer]`r`nZoneId=3" | Set-Content -LiteralPath "$($_.FullName):Zone.Identifier" -Encoding ascii
}
Test-PackagedStartup "Downloaded-package"
New-Item -ItemType Directory -Path $packagingRoot -Force | Out-Null
$dist | Set-Content -LiteralPath (Join-Path $packagingRoot "latest.txt") -Encoding utf8
