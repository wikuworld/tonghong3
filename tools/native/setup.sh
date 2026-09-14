#!/usr/bin/env bash
# Siapkan venv Python + npm, tanpa Docker.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${PYTHON:-python3.11}"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Butuh $PY (EL8: python3.11). Tidak ditemukan." >&2
  exit 1
fi

echo "==> Backend venv ($PY)"
if [[ ! -x "$ROOT/backend/.venv/bin/python" ]]; then
  "$PY" -m venv "$ROOT/backend/.venv"
fi
"$ROOT/backend/.venv/bin/pip" install -q --upgrade pip
"$ROOT/backend/.venv/bin/pip" install -q -r "$ROOT/backend/requirements.txt"

echo "==> MRP venv ($PY)"
if [[ ! -x "$ROOT/mrp/.venv/bin/python" ]]; then
  "$PY" -m venv "$ROOT/mrp/.venv"
fi
"$ROOT/mrp/.venv/bin/pip" install -q --upgrade pip
"$ROOT/mrp/.venv/bin/pip" install -q -r "$ROOT/mrp/requirements.txt"

echo "==> Frontend npm"
if [[ -s "$ROOT/tools/nvm-load.sh" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/tools/nvm-load.sh" || true
fi
(
  cd "$ROOT/frontend"
  npm install
)

chmod +x "$ROOT/tools/native/"*.sh
echo "==> Setup native selesai."
echo "    Install systemd: $ROOT/tools/native/install-systemd.sh --start"
