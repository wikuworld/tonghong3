#!/usr/bin/env bash
# Salin unit systemd ke /etc/systemd/system dan (opsional) start.
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
  "$UNIT_DIR/tonghong-backend.service" \
  "$UNIT_DIR/tonghong-mrp.service" \
  "$UNIT_DIR/tonghong-frontend.service" \
  "$UNIT_DIR/tonghong.target" \
  /etc/systemd/system/

systemctl daemon-reload
systemctl enable tonghong-mrp.service tonghong-backend.service tonghong-frontend.service tonghong.target

if [[ "$START" -eq 1 ]]; then
  systemctl restart tonghong-mrp.service tonghong-backend.service tonghong-frontend.service
  systemctl --no-pager --full status tonghong-mrp.service tonghong-backend.service tonghong-frontend.service || true
fi

echo "==> Unit terpasang: tonghong-mrp, tonghong-backend, tonghong-frontend, tonghong.target"
echo "    Status: systemctl status tonghong.target"
echo "    Log:    journalctl -u tonghong-backend -u tonghong-mrp -u tonghong-frontend -f"
