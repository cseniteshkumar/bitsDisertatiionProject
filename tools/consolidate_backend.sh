#!/usr/bin/env bash
set -euo pipefail

# Consolidation helper: make `backend` the canonical package backed by
# `gpt_researcher`, archive duplicate agent folders, and update imports.
#
# IMPORTANT: this script makes in-place edits. Review and run from repo root.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "Archiving duplicate folders (if present)..."
mkdir -p archive
for d in multi_agents deep_agents; do
  if [ -d "$d" ]; then
    echo "Moving $d -> archive/$d"
    mv "$d" archive/
  fi
done

echo "Updating imports: replacing 'from gpt_researcher' and 'import gpt_researcher' with 'backend' in project files (excluding gpt_researcher/)..."
# Find files referencing gpt_researcher but skip the gpt_researcher tree and .venv
grep -RIn --exclude-dir=gpt_researcher --exclude-dir=.venv --exclude-dir=archive "gpt_researcher" . | cut -d: -f1 | sort -u | while read -r file; do
  echo "Updating: $file"
  sed -i "s/from gpt_researcher/from backend/g" "$file" || true
  sed -i "s/import gpt_researcher/import backend/g" "$file" || true
  sed -i "s/gpt_researcher\./backend./g" "$file" || true
done

echo "Consolidation script finished. Please run tests and review changes before committing."
