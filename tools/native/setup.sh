#!/usr/bin/env bash
# Siapkan venv Python + npm, tanpa Docker.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${PYTHON:-python3.11}"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Butuh $PY (EL8: python3.11). Tidak ditemukan." >&2
  exit 1
fi

echo "==> ERP API venv ($PY)"
if [[ ! -x "$ROOT/erp/backend/.venv/bin/python" ]]; then
  "$PY" -m venv "$ROOT/erp/backend/.venv"
fi
"$ROOT/erp/backend/.venv/bin/pip" install -q --upgrade pip
"$ROOT/erp/backend/.venv/bin/pip" install -q -r "$ROOT/erp/backend/requirements.txt"

echo "==> MRP API venv ($PY)"
if [[ ! -x "$ROOT/mrp/backend/.venv/bin/python" ]]; then
  "$PY" -m venv "$ROOT/mrp/backend/.venv"
fi
"$ROOT/mrp/backend/.venv/bin/pip" install -q --upgrade pip
"$ROOT/mrp/backend/.venv/bin/pip" install -q -r "$ROOT/mrp/backend/requirements.txt"

echo "==> ERP + MRP frontend npm"
if [[ -s "$ROOT/tools/nvm-load.sh" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/tools/nvm-load.sh" || true
fi
(
  cd "$ROOT/erp/frontend"
  npm install
)
(
  cd "$ROOT/mrp/frontend"
  npm install
)

chmod +x "$ROOT/tools/native/"*.sh
echo "==> Setup native selesai."
echo "    Install systemd UAT: $ROOT/tools/native/install-systemd-tonghong-uat.sh --start"
