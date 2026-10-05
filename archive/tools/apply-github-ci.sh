#!/usr/bin/env bash
# Terapkan CI workflow ke .github/workflows/ci.yml lalu push (butuh gh token scope workflow).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cp "$ROOT/tools/github-ci.yml" "$ROOT/.github/workflows/ci.yml"
rm -f "$ROOT/.github/workflows/cd-ghcr.yml"
echo "Copied tools/github-ci.yml → .github/workflows/ci.yml"
echo "Refresh token: gh auth refresh -h github.com -s workflow"
echo "Then: git add .github/workflows && git commit -m 'chore(ci): sync workflow from tools/github-ci.yml' && git push"
