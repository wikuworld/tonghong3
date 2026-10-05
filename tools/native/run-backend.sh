#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/tools/native/load-env.sh"

cd "$ROOT/erp/backend"
VENV="$ROOT/erp/backend/.venv"
if [[ ! -x "$VENV/bin/uvicorn" ]]; then
  echo "Backend venv belum siap. Jalankan: $ROOT/tools/native/setup.sh" >&2
  exit 1
fi

if [[ "${TONGHONG_SKIP_ALEMBIC:-0}" != "1" ]]; then
  "$VENV/bin/alembic" upgrade head
fi
# Satu listener di BACKEND_PORT (hindari 500 dari proxy UI bila proses manual masih hidup).
if [[ "${TONGHONG_FREE_PORT_BEFORE_START:-1}" == "1" ]] && command -v fuser >/dev/null 2>&1; then
  fuser -k "${BACKEND_PORT}/tcp" 2>/dev/null || true
  sleep 1
fi
exec "$VENV/bin/uvicorn" app.main:app \
  --host 0.0.0.0 \
  --port "${BACKEND_PORT}" \
  --loop asyncio
