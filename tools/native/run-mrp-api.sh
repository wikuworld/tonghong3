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

cd "$ROOT/mrp/backend"
VENV="$ROOT/mrp/backend/.venv"
if [[ ! -x "$VENV/bin/uvicorn" ]]; then
  echo "MRP API venv belum siap. Jalankan: python3.12 -m venv $VENV && $VENV/bin/pip install -r $ROOT/mrp/backend/requirements.txt" >&2
  exit 1
fi

export DATABASE_URL="${DATABASE_URL:-mysql+pymysql://uat_tonghong_mrp:UatTonghongMrp2026@127.0.0.1:3306/uat_tonghong_mrp}"
export MRP_JWT_SECRET="${MRP_JWT_SECRET:-uat-mrp-jwt-secret-2026}"
export ERP_API_URL="${ERP_API_URL:-http://127.0.0.1:8001}"
export ERP_SERVICE_TOKEN="${ERP_SERVICE_TOKEN:-dev-erp-service-token-change-me}"
# Pastikan tidak ada koneksi SQL lintas-DB ke ERP
unset ERP_DATABASE_URL ERP_DB_HOST ERP_DB_PORT ERP_DB_NAME ERP_DB_USER ERP_DB_PASSWORD MRP_ERP_ACCESS 2>/dev/null || true

exec "$VENV/bin/uvicorn" mrp_api.main:app \
  --host 0.0.0.0 \
  --port "${MRP_API_PORT:-8002}" \
  --loop asyncio
