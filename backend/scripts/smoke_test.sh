#!/usr/bin/env bash
# Smoke test semua skrip di backend/scripts/
#
# Usage:
#   ./backend/scripts/smoke_test.sh
#   ./backend/scripts/smoke_test.sh --verbose
#   ./backend/scripts/smoke_test.sh --only normalize_lot_numbers
#
# Otomatis pakai container backend bila stack Docker aktif.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND="$ROOT/backend"
cd "$ROOT"

run_in_backend() {
  if command -v docker >/dev/null 2>&1; then
    if docker compose ps --status running backend 2>/dev/null | grep -q backend; then
      exec docker compose exec -T backend python scripts/smoke_test.py "$@"
    fi
    if sudo -n docker compose ps --status running backend 2>/dev/null | grep -q backend; then
      exec sudo docker compose exec -T backend python scripts/smoke_test.py "$@"
    fi
  fi

  cd "$BACKEND"
  export PYTHONPATH=.
  exec python3 scripts/smoke_test.py "$@"
}

run_in_backend "$@"
