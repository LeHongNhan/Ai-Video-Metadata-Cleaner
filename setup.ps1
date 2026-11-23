$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
py -3.12 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 with the Python Launcher first.' }
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
Write-Host 'Ready. Put ffmpeg.exe and ffprobe.exe in tools, then run run.ps1.'
