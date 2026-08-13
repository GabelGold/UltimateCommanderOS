@echo off
setlocal
cd /d "%~dp0"
echo [UCOS] git pull...
git pull --rebase --autostash
if exist "venv\Scripts\python.exe" (
  "venv\Scripts\python.exe" -m pip install -r requirements.txt
) else (
  py -3.12 -m pip install -r requirements.txt
)
echo [UCOS] restart
call "%~dp0start.bat"
