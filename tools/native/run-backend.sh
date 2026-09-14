#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/tools/native/load-env.sh"

cd "$ROOT/backend"
VENV="$ROOT/backend/.venv"
if [[ ! -x "$VENV/bin/uvicorn" ]]; then
  echo "Backend venv belum siap. Jalankan: $ROOT/tools/native/setup.sh" >&2
  exit 1
fi

if [[ "${TONGHONG_SKIP_ALEMBIC:-0}" != "1" ]]; then
  "$VENV/bin/alembic" upgrade head
fi
exec "$VENV/bin/uvicorn" app.main:app \
  --host 0.0.0.0 \
  --port "${BACKEND_PORT}" \
  --loop asyncio
