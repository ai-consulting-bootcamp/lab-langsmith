@echo off
REM Analyse saved results and redraw the figures (free)
cd /d "%~dp0"
python analyze_results.py 
echo.
pause
