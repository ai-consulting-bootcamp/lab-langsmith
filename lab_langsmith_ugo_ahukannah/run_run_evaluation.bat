@echo off
REM Run all three LangSmith experiments (~$0.14)
cd /d "%~dp0"
python run_evaluation.py --targets mini,gpt4o,terse
echo.
pause
