#!/usr/bin/env bash
set -e

# Folders
mkdir -p data notebooks results

# Root files (won't overwrite if they already exist)
for f in README.md lab_proof.md evaluation_summary.md optimization_summary.md; do
  [ -f "$f" ] || echo "# ${f%.md}" | sed 's/_/ /g' > "$f"
done

# Data + notebook placeholders
[ -f data/examples.json ] || echo "[]" > data/examples.json
[ -f notebooks/langsmith_gdpr_eval.ipynb ] || cat > notebooks/langsmith_gdpr_eval.ipynb <<'EOF'
{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
EOF

# Keep empty results/ in git
touch results/.gitkeep

# .env template (never committed)
[ -f .env ] || cat > .env <<'EOF'
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_PROJECT=gdpr-qa-eval
OPENAI_API_KEY=
EOF

# Ignore secrets and clutter
for line in ".env" "__pycache__/" ".ipynb_checkpoints/"; do
  grep -qxF "$line" .gitignore 2>/dev/null || echo "$line" >> .gitignore
done

echo "Done:"; find . -path ./.git -prune -o -print | sort