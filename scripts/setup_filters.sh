#!/usr/bin/env bash
# ghmath filters setup — register the clean/smudge filters in git config.
# Run once per clone:
#   bash scripts/setup_filters.sh
# Requires: python on PATH. The scripts use `python`, fall back to `python3`.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=""
if command -v python >/dev/null 2>&1; then
  PY="python"
elif command -v python3 >/dev/null 2>&1; then
  PY="python3"
else
  echo "ERROR: python not found" >&2
  exit 1
fi

git config filter.ghmath.clean  "\"$PY\" \"$HERE/ghmath_clean.py\""
git config filter.ghmath.smudge "\"$PY\" \"$HERE/ghmath_smudge.py\""

echo "filter.ghmath configured:"
git config --get filter.ghmath.clean
git config --get filter.ghmath.smudge
echo "Done. Working tree will stay Obsidian-friendly; commits get GitHub-correct math."
