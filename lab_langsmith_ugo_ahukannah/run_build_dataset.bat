@echo off
REM Build and validate the evaluation dataset (no API calls, free)
cd /d "%~dp0"
python build_dataset.py 
echo.
pause
