#!/usr/bin/env bash
# Jalankan pipeline CI lokal (mirror tools/github-ci.yml) tanpa GitHub Actions.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Frontend: lint + test + build =="
(cd frontend && npm ci && npm run lint && npm run test && npm run build)

echo "== Backend: ruff + pytest =="
(cd backend && pip install -q -r requirements.txt && python -m ruff check --select F,E9 app tests && python -m pytest -q)

echo "== Native: health smoke =="
curl -fsS http://localhost:8000/health | grep -q '"status":"ok"'
curl -fsS http://localhost:8080/ >/dev/null
(cd backend && PYTHONPATH=. .venv/bin/python scripts/smoke_test.py)

echo "✅ CI lokal selesai"
