$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$release = Join-Path $root "release"
$latest = Join-Path $root ".packaging\latest.txt"
if (-not (Test-Path $latest)) { throw "Run scripts\build.ps1 before packaging." }
$app = (Get-Content -LiteralPath $latest -Raw).Trim()
$stage = Join-Path $release "package-alpha.29"
$zip = Join-Path $release "ip-commandmic-lab-0.1.0-alpha.29-windows-x64.zip"
$checksum = "$zip.sha256"

if (-not (Test-Path (Join-Path $app "IPCommandMicLab.exe"))) {
    throw "Run scripts\build.ps1 before packaging."
}

if (Test-Path $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
if (Test-Path $zip) { Remove-Item -LiteralPath $zip -Force }
if (Test-Path $checksum) { Remove-Item -LiteralPath $checksum -Force }

New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item -LiteralPath $app -Destination (Join-Path $stage "IPCommandMicLab") -Recurse
Copy-Item -LiteralPath (Join-Path $root "README.md") -Destination $stage
Copy-Item -LiteralPath (Join-Path $root "LICENSE") -Destination $stage
Copy-Item -LiteralPath (Join-Path $root "NOTICE.md") -Destination $stage
Copy-Item -LiteralPath (Join-Path $root "RELEASE_NOTES.md") -Destination $stage
Copy-Item -LiteralPath (Join-Path $root "RELEASE_READINESS.md") -Destination $stage

Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip -CompressionLevel Optimal
$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $zip).Hash.ToLowerInvariant()
"$hash  $(Split-Path -Leaf $zip)" | Set-Content -LiteralPath $checksum -Encoding ascii
Write-Output $zip
Write-Output $checksum
