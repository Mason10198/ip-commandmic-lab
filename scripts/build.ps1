$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$packagingRoot = Join-Path $root ".packaging"
$buildId = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$staging = Join-Path $packagingRoot $buildId
& $python -m PyInstaller --noconfirm --clean --onedir --windowed --optimize 2 `
  --name IPCommandMicLab --paths (Join-Path $root "src") `
  --collect-data ip_commandmic_lab `
  --hidden-import ip_commandmic.display --hidden-import ip_commandmic.test_app `
  --distpath (Join-Path $staging "dist") --workpath (Join-Path $staging "build") `
  --specpath $staging `
  (Join-Path $PSScriptRoot "entry.py")
if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }
$dist = Join-Path $staging "dist\IPCommandMicLab"
$smoke = Start-Process -FilePath (Join-Path $dist "IPCommandMicLab.exe") `
  -ArgumentList "--package-smoke-test" -Wait -PassThru -WindowStyle Hidden
if ($smoke.ExitCode -ne 0) { throw "Packaged startup smoke test failed with exit code $($smoke.ExitCode)" }
New-Item -ItemType Directory -Path $packagingRoot -Force | Out-Null
$dist | Set-Content -LiteralPath (Join-Path $packagingRoot "latest.txt") -Encoding utf8
