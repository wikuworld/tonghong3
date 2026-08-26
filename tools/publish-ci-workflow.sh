#!/usr/bin/env bash
# Terapkan dan push workflow GitHub Actions (butuh: gh auth refresh -s workflow).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! gh auth status 2>&1 | grep -q "workflow"; then
  echo "Token belum punya scope workflow."
  echo "Jalankan: gh auth refresh -h github.com -s workflow"
  echo "Lalu buka https://github.com/login/device dan masukkan kode yang ditampilkan."
  exit 1
fi

"$ROOT/tools/apply-github-ci.sh"
git checkout ui/elementplus-consistency
git pull origin ui/elementplus-consistency
git checkout -B chore/apply-ci-workflow
git add .github/workflows/
git diff --cached --quiet && echo "Tidak ada perubahan workflow." && exit 0
git commit -m "chore(ci): terapkan workflow vitest dan pytest"
git push -u origin chore/apply-ci-workflow --force-with-lease
gh pr create --head chore/apply-ci-workflow --base ui/elementplus-consistency \
  --title "chore(ci): terapkan workflow GitHub Actions" \
  --body "Terapkan tools/github-ci.yml ke .github/workflows/ci.yml" || true
gh pr merge chore/apply-ci-workflow --merge --delete-branch || git push origin ui/elementplus-consistency
echo "✅ Workflow dipublish"
