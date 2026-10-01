@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" tools\phone_preview.py --stop
echo.
pause
