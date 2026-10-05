#!/usr/bin/env bash
# Pasang 4 unit produk UAT. Jangan menyentuh unit live tonghong-*.
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

UNITS=(
  tonghong-uat-erp-api.service
  tonghong-uat-erp-ui.service
  tonghong-uat-mrp-api.service
  tonghong-uat-mrp-ui.service
  tonghong-uat.target
)

copy_units() {
  local files=()
  local u
  for u in "${UNITS[@]}"; do
    files+=("$UNIT_DIR/$u")
  done
  install -m 0644 "${files[@]}" /etc/systemd/system/
}

enable_units() {
  systemctl daemon-reload
  systemctl enable "${UNITS[@]}"
  systemctl disable tonghong-uat-backend.service tonghong-uat-frontend.service tonghong-uat-mrp.service 2>/dev/null || true
}

if [[ "$(id -u)" -eq 0 ]]; then
  copy_units
  enable_units
  if [[ "$START" -eq 1 ]]; then
    systemctl restart tonghong-uat-mrp-api.service tonghong-uat-mrp-ui.service
    systemctl restart tonghong-uat-erp-api.service tonghong-uat-erp-ui.service
    systemctl --no-pager --full status tonghong-uat-mrp-api.service tonghong-uat-erp-api.service || true
  fi
else
  sudo install -m 0644 \
    "$UNIT_DIR/tonghong-uat-erp-api.service" \
    "$UNIT_DIR/tonghong-uat-erp-ui.service" \
    "$UNIT_DIR/tonghong-uat-mrp-api.service" \
    "$UNIT_DIR/tonghong-uat-mrp-ui.service" \
    "$UNIT_DIR/tonghong-uat.target" \
    /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable "${UNITS[@]}"
  sudo systemctl disable tonghong-uat-backend.service tonghong-uat-frontend.service tonghong-uat-mrp.service 2>/dev/null || true
  if [[ "$START" -eq 1 ]]; then
    sudo systemctl restart tonghong-uat-mrp-api.service tonghong-uat-mrp-ui.service
    sudo systemctl restart tonghong-uat-erp-api.service tonghong-uat-erp-ui.service
    systemctl --no-pager --full status tonghong-uat-mrp-api.service tonghong-uat-erp-api.service || true
  fi
fi

echo "==> Unit terpasang: tonghong-uat-erp-api/ui, tonghong-uat-mrp-api/ui, tonghong-uat.target"
echo "    ERP UI : http://127.0.0.1:8081"
echo "    ERP API: http://127.0.0.1:8001/docs"
echo "    MRP UI : http://127.0.0.1:8082"
echo "    MRP API: http://127.0.0.1:8002/health"
echo "    Live (jangan disentuh): tonghong-backend / tonghong-mrp / tonghong-frontend"
