#!/bin/sh
set -eu

HOST="${MRP_DB_HOST:-mariadb}"
PORT="${MRP_DB_PORT:-3306}"
ROOT_USER="${MRP_DB_ROOT_USER:-root}"
ROOT_PASS="${MYSQL_ROOT_PASSWORD:-${MRP_DB_ROOT_PASSWORD:-root}}"
DB_NAME="${MRP_DB_NAME:-tonghong_mrp}"
DB_USER="${MRP_DB_USER:-tonghong_mrp}"
DB_PASS="${MRP_DB_PASSWORD:-tonghong_mrp_secret}"
SEED_FILE="${MRP_SEED_FILE:-/app/seed/tonghong_mrp.sql}"

echo "[mrp] waiting for MariaDB at ${HOST}:${PORT}..."
i=0
until mysqladmin ping -h"$HOST" -P"$PORT" -u"$ROOT_USER" -p"$ROOT_PASS" --silent 2>/dev/null; do
  i=$((i + 1))
  if [ "$i" -ge 60 ]; then
    echo "[mrp] MariaDB not ready after 60s" >&2
    exit 1
  fi
  sleep 2
done
echo "[mrp] MariaDB is up"

echo "[mrp] ensuring database ${DB_NAME} and user ${DB_USER}"
mysql -h"$HOST" -P"$PORT" -u"$ROOT_USER" -p"$ROOT_PASS" <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASS}';
ALTER USER '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'%';
FLUSH PRIVILEGES;
SQL

TABLE_COUNT=$(mysql -h"$HOST" -P"$PORT" -u"$ROOT_USER" -p"$ROOT_PASS" -N -e \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${DB_NAME}'")

if [ "${TABLE_COUNT:-0}" = "0" ]; then
  if [ -f "$SEED_FILE" ]; then
    echo "[mrp] importing seed ${SEED_FILE}"
    mysql -h"$HOST" -P"$PORT" -u"$ROOT_USER" -p"$ROOT_PASS" "$DB_NAME" < "$SEED_FILE"
  else
    echo "[mrp] seed missing; running init_db.py / schema.sql"
    python /app/init_db.py || true
  fi
else
  echo "[mrp] database already has ${TABLE_COUNT} tables; skip seed"
fi

PORT_APP="${MRP_PORT:-5010}"
echo "[mrp] starting Flask on 0.0.0.0:${PORT_APP}"
exec python -c "from app import app; app.run(host='0.0.0.0', port=${PORT_APP}, debug=False)"
