$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run setup.ps1 first.' }
& $python -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
& $python -m PyInstaller --noconfirm VideoConverter.spec
if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
Write-Host 'Built: dist/AI Video Metadata Cleaner/AI Video Metadata Cleaner.exe'
