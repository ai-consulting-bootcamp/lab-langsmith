#!/bin/bash
# Analyse saved results and redraw the figures (free)
cd "$(dirname "$0")"
PY=/opt/homebrew/Caskroom/miniconda/base/envs/bootcamp-env/bin/python
[ -x "$PY" ] || PY=python3
"$PY" analyze_results.py 
echo
echo "Press any key to close..."
read -n 1 -s
