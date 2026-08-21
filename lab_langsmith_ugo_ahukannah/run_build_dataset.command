#!/bin/bash
# Build and validate the evaluation dataset (no API calls, free)
cd "$(dirname "$0")"
PY=/opt/homebrew/Caskroom/miniconda/base/envs/bootcamp-env/bin/python
[ -x "$PY" ] || PY=python3
"$PY" build_dataset.py 
echo
echo "Press any key to close..."
read -n 1 -s
