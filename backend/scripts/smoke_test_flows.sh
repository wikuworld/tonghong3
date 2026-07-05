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
  if command -v docker >/dev/null 2>&1; then
    if docker compose ps --status running backend 2>/dev/null | grep -q backend; then
      exec docker compose exec -T backend python scripts/smoke_test_flows.py "$@"
    fi
    if sudo -n docker compose ps --status running backend 2>/dev/null | grep -q backend; then
      exec sudo docker compose exec -T backend python scripts/smoke_test_flows.py "$@"
    fi
  fi

  cd "$BACKEND"
  export PYTHONPATH=.
  exec python3 scripts/smoke_test_flows.py "$@"
}

run_in_backend "$@"
