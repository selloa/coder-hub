@echo off
cd /d "%~dp0"
python build.py
if errorlevel 1 exit /b 1
echo.
echo Serving at http://localhost:8000/
echo Press Ctrl+C to stop.
start http://localhost:8000/
python -m http.server 8000
