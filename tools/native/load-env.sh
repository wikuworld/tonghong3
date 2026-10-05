# shellcheck shell=bash
# Muat /tonghong/.env ke environment proses (dipakai run-*.sh).
# Source file ini; jangan di-exec.

_NATIVE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
_ENV_FILE="${TONGHONG_ENV_FILE:-$_NATIVE_ROOT/.env}"

if [[ -f "$_ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$_ENV_FILE"
  set +a
fi

# Hostname Docker `mrp` tidak resolve di host — pakai loopback.
if [[ "${MRP_UPSTREAM_URL:-}" == *"mrp:"* ]]; then
  export MRP_UPSTREAM_URL="http://127.0.0.1:${MRP_PORT:-5010}"
fi
export MRP_UPSTREAM_URL="${MRP_UPSTREAM_URL:-http://127.0.0.1:8002}"
export MRP_PORT="${MRP_PORT:-8002}"
export BACKEND_PORT="${BACKEND_PORT:-8001}"
export WEB_PORT="${WEB_PORT:-8081}"
export VITE_API_PROXY="${VITE_API_PROXY:-http://127.0.0.1:${BACKEND_PORT}}"
export PYTHONUNBUFFERED=1
