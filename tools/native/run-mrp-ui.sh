#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/tools/native/load-env.sh"
if [[ -f "$ROOT/mrp/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/mrp/.env"
  set +a
fi
if [[ -s "$ROOT/tools/nvm-load.sh" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/tools/nvm-load.sh"
fi
if command -v nvm >/dev/null 2>&1; then
  nvm use 22 >/dev/null
fi

cd "$ROOT/mrp/frontend"
if [[ ! -x "$ROOT/mrp/frontend/node_modules/.bin/vite" ]]; then
  echo "MRP frontend node_modules belum siap. Jalankan npm install di $ROOT/mrp/frontend" >&2
  exit 1
fi

export WEB_PORT="${WEB_PORT:-8082}"
export VITE_API_PROXY="${VITE_API_PROXY:-http://127.0.0.1:8002}"
export VITE_HMR_PORT="${VITE_HMR_PORT:-$WEB_PORT}"
export VITE_HMR_CLIENT_PORT="${VITE_HMR_CLIENT_PORT:-$WEB_PORT}"
export PATH="$ROOT/mrp/frontend/node_modules/.bin:${NVM_DIR:-$HOME/.nvm}/versions/node/v22.23.2/bin:/usr/local/bin:/usr/bin:$PATH"

exec npm run dev -- --host 0.0.0.0 --port "${WEB_PORT}"
