#!/usr/bin/env bash
# Smoke test alur PO, marketing flow, delivery, outstanding
#
# Usage:
#   ./backend/scripts/smoke_test_flows.sh
#   ./backend/scripts/smoke_test_flows.sh --verbose
#   ./backend/scripts/smoke_test_flows.sh --read-only

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND="$ROOT/backend"
cd "$ROOT"

run_in_backend() {
  cd "$BACKEND"
  export PYTHONPATH=.
  if [[ -x .venv/bin/python ]]; then
    exec .venv/bin/python scripts/smoke_test_flows.py "$@"
  fi
  exec python3 scripts/smoke_test_flows.py "$@"
}

run_in_backend "$@"
