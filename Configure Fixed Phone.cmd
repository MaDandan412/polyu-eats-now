@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -u tools\tailscale_phone.py --enable
echo.
pause
