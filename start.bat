@echo off
setlocal
cd /d "%~dp0"
set UCOS_SKIP_VENV=0
if exist "venv\Scripts\pythonw.exe" (
  start "" "venv\Scripts\pythonw.exe" "%~dp0ultimate_commander.py"
  exit /b 0
)
if exist "dist\UltimateCommanderOS\UltimateCommanderOS.exe" (
  start "" "dist\UltimateCommanderOS\UltimateCommanderOS.exe"
  exit /b 0
)
py -3.12 "%~dp0ultimate_commander.py"
