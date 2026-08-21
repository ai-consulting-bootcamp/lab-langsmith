#!/bin/bash
# Run all three LangSmith experiments (~$0.14)
cd "$(dirname "$0")"
PY=/opt/homebrew/Caskroom/miniconda/base/envs/bootcamp-env/bin/python
[ -x "$PY" ] || PY=python3
"$PY" run_evaluation.py --targets mini,gpt4o,terse
echo
echo "Press any key to close..."
read -n 1 -s
