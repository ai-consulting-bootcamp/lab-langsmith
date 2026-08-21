@echo off
REM Run the evaluator controls (~$0.001)
cd /d "%~dp0"
python evaluators.py 
echo.
pause
