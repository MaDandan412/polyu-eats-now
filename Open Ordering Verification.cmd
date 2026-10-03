@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run start.ps1 -Setup first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "tools\open_ordering_verification.py"
pause
