# Windows release packaging

This directory is for maintainers building the portable Windows release. End
users should follow the [Windows quick start](../../README.md#windows-quick-start)
and download the prebuilt ZIP from GitHub Releases.

From the repository root, run `scripts\build.ps1` and then
`scripts\package.ps1`. The scripts build the PyInstaller application directory,
run the frozen native-backend startup smoke check, and create the distributable
ZIP plus its SHA-256 checksum under `release\`.
