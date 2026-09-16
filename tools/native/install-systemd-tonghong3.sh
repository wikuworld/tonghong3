#!/usr/bin/env bash
# Salin unit systemd tonghong3 ke /etc/systemd/system dan (opsional) start.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UNIT_DIR="$ROOT/tools/native/systemd"
START=0
for arg in "$@"; do
  case "$arg" in
    --start) START=1 ;;
    -h|--help)
      echo "Usage: $0 [--start]"
      exit 0
      ;;
  esac
done

if [[ ! -d /etc/systemd/system ]]; then
  echo "systemd tidak tersedia di host ini." >&2
  exit 1
fi

install -m 0644 \
  "$UNIT_DIR/tonghong3-backend.service" \
  "$UNIT_DIR/tonghong3-mrp.service" \
  "$UNIT_DIR/tonghong3-frontend.service" \
  "$UNIT_DIR/tonghong3.target" \
  /etc/systemd/system/

systemctl daemon-reload
systemctl enable tonghong3-mrp.service tonghong3-backend.service tonghong3-frontend.service tonghong3.target

if [[ "$START" -eq 1 ]]; then
  systemctl restart tonghong3-mrp.service tonghong3-backend.service tonghong3-frontend.service
  systemctl --no-pager --full status tonghong3-mrp.service tonghong3-backend.service tonghong3-frontend.service || true
fi

echo "==> Unit terpasang: tonghong3-mrp, tonghong3-backend, tonghong3-frontend, tonghong3.target"
echo "    UI+API : http://127.0.0.1:${WEB_PORT:-8081}"
echo "    API    : http://127.0.0.1:${BACKEND_PORT:-8001}/docs"
echo "    MRP    : http://127.0.0.1:${MRP_PORT:-5011}/"
echo "    Status: systemctl status tonghong3.target"
echo "    Log:    journalctl -u tonghong3-backend -u tonghong3-mrp -u tonghong3-frontend -f"
