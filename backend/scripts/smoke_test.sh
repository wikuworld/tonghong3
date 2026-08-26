#!/usr/bin/env bash
# Smoke test semua skrip di backend/scripts/
#
# Usage:
#   ./backend/scripts/smoke_test.sh
#   ./backend/scripts/smoke_test.sh --verbose
#   ./backend/scripts/smoke_test.sh --only normalize_lot_numbers
#
# Otomatis pakai venv backend bila ada.


set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND="$ROOT/backend"
cd "$ROOT"

run_in_backend() {
  cd "$BACKEND"
  export PYTHONPATH=.
  if [[ -x .venv/bin/python ]]; then
    exec .venv/bin/python scripts/smoke_test.py "$@"
  fi
  exec python3 scripts/smoke_test.py "$@"
}

run_in_backend "$@"
