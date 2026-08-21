#!/bin/bash
# Run the evaluator controls (~$0.001)
cd "$(dirname "$0")"
PY=/opt/homebrew/Caskroom/miniconda/base/envs/bootcamp-env/bin/python
[ -x "$PY" ] || PY=python3
"$PY" evaluators.py 
echo
echo "Press any key to close..."
read -n 1 -s
