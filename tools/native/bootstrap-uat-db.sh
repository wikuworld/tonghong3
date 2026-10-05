#!/usr/bin/env bash
# Create UAT schemas/users on local MariaDB. Never touches tonghong / tonghong_mrp.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SQL="$ROOT/tools/native/create-uat-databases.sql"
DUMP_ERP="$ROOT/database/tonghong-20260915-223724.sql"
DUMP_MRP="$ROOT/database/tonghong_mrp-20260915-223724.sql"

mysql_admin() {
  if [[ "$(id -u)" -eq 0 ]]; then
    mysql --protocol=socket "$@"
    return
  fi
  if sudo -n mysql --protocol=socket -e "SELECT 1" >/dev/null 2>&1; then
    sudo -n mysql --protocol=socket "$@"
    return
  fi
  if [[ -n "${SUDO_ASKPASS:-}" && -x "${SUDO_ASKPASS}" ]]; then
    sudo -A mysql --protocol=socket "$@"
    return
  fi
  sudo mysql --protocol=socket "$@"
}

echo "==> live baseline (read-only)"
mysql -h 127.0.0.1 -utonghong -ptonghong_secret -N -e \
  "SELECT 'live_tonghong_tables', COUNT(*) FROM information_schema.tables WHERE table_schema='tonghong'; SELECT 'live_tonghong_users', COUNT(*) FROM tonghong.users;"
mysql -h 127.0.0.1 -utonghong_mrp -ptonghong_mrp_secret -N -e \
  "SELECT 'live_tonghong_mrp_tables', COUNT(*) FROM information_schema.tables WHERE table_schema='tonghong_mrp';"

echo "==> create UAT databases/users"
mysql_admin < "$SQL"

echo "==> import dumps into uat_* only"
mysql_admin uat_tonghong_erp < "$DUMP_ERP"
mysql_admin uat_tonghong_mrp < "$DUMP_MRP"

echo "==> alembic upgrade uat_tonghong_erp"
# shellcheck disable=SC1091
source "$ROOT/tools/native/load-env.sh"
cd "$ROOT/erp/backend"
"$ROOT/erp/backend/.venv/bin/alembic" upgrade head

echo "==> verify isolation"
mysql -h 127.0.0.1 -utonghong -ptonghong_secret -N -e \
  "SELECT 'live_tonghong_tables', COUNT(*) FROM information_schema.tables WHERE table_schema='tonghong'; SELECT 'live_tonghong_users', COUNT(*) FROM tonghong.users;"
mysql -h 127.0.0.1 -utonghong_mrp -ptonghong_mrp_secret -N -e \
  "SELECT 'live_tonghong_mrp_tables', COUNT(*) FROM information_schema.tables WHERE table_schema='tonghong_mrp';"
mysql -h 127.0.0.1 -uuat_tonghong_erp -pUatTonghongErp2026 -N -e \
  "SELECT 'uat_erp_tables', COUNT(*) FROM information_schema.tables WHERE table_schema='uat_tonghong_erp';"
mysql -h 127.0.0.1 -uuat_tonghong_mrp -pUatTonghongMrp2026 -N -e \
  "SELECT 'uat_mrp_tables', COUNT(*) FROM information_schema.tables WHERE table_schema='uat_tonghong_mrp';"

echo "==> UAT databases ready"
