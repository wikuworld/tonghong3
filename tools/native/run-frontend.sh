#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/tools/native/load-env.sh"

cd "$ROOT/frontend"
if [[ ! -x "$ROOT/frontend/node_modules/.bin/vite" ]]; then
  echo "Frontend node_modules belum siap. Jalankan: $ROOT/tools/native/setup.sh" >&2
  exit 1
fi

export VITE_API_PROXY="${VITE_API_PROXY:-http://127.0.0.1:${BACKEND_PORT}}"
export VITE_HMR_PORT="${VITE_HMR_PORT:-$WEB_PORT}"
export VITE_HMR_CLIENT_PORT="${VITE_HMR_CLIENT_PORT:-$WEB_PORT}"
export PATH="$ROOT/frontend/node_modules/.bin:/usr/local/bin:/usr/bin:$PATH"

exec npm run dev -- --host 0.0.0.0 --port "${WEB_PORT}"
