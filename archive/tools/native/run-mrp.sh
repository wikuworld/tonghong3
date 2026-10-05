#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/tools/native/load-env.sh"

cd "$ROOT/mrp"
VENV="$ROOT/mrp/.venv"
if [[ ! -x "$VENV/bin/python" ]]; then
  echo "MRP venv belum siap. Jalankan: $ROOT/tools/native/setup.sh" >&2
  exit 1
fi

exec "$VENV/bin/python" app.py
