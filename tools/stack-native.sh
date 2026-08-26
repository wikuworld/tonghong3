#!/usr/bin/env bash
# Start/stop/status stack Tonghong native (systemd).
# Usage: ./tools/stack-native.sh {start|stop|restart|status|logs}
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNITS=(mariadb nginx tonghong-backend tonghong-mrp tonghong-frontend)
APP_UNITS=(tonghong-backend tonghong-mrp tonghong-frontend)

need_sudo() {
  if [[ "$(id -u)" -eq 0 ]]; then
    return 0
  fi
  if [[ -n "${SUDO_ASKPASS:-}" && -x "${SUDO_ASKPASS}" ]]; then
    sudo -A -p '' -v
  else
    sudo -v
  fi
}

cmd_start() {
  need_sudo
  sudo systemctl start mariadb
  sudo systemctl start tonghong-backend tonghong-mrp
  sudo systemctl start tonghong-frontend
  sudo systemctl start nginx
  sudo systemctl reload nginx
  cmd_status
}

cmd_stop() {
  need_sudo
  sudo systemctl stop tonghong-frontend tonghong-backend tonghong-mrp nginx || true
}

cmd_restart() {
  cmd_stop
  cmd_start
}

cmd_status() {
  echo "==> Tonghong native"
  systemctl is-active mariadb nginx "${APP_UNITS[@]}" 2>/dev/null | awk '
    BEGIN { n=0; split("mariadb nginx tonghong-backend tonghong-mrp tonghong-frontend", u) }
    { n++; printf "  %-22s %s\n", u[n], $0 }
  ' || true
  echo ""
  echo "UI+API : http://127.0.0.1:8080"
  echo "API    : http://127.0.0.1:8000/docs"
  echo "Health : http://127.0.0.1:8000/health"
}

cmd_logs() {
  need_sudo
  sudo journalctl -u tonghong-backend -u tonghong-mrp -u tonghong-frontend -u nginx -f
}

cmd_install() {
  need_sudo
  sudo cp "$ROOT/deploy/systemd/tonghong-backend.service" /etc/systemd/system/
  sudo cp "$ROOT/deploy/systemd/tonghong-mrp.service" /etc/systemd/system/
  sudo cp "$ROOT/deploy/systemd/tonghong-frontend.service" /etc/systemd/system/
  sudo cp "$ROOT/frontend/nginx.native.conf" /etc/nginx/sites-available/tonghong-native
  sudo ln -sfn /etc/nginx/sites-available/tonghong-native /etc/nginx/sites-enabled/tonghong-native
  if [[ -e /etc/nginx/sites-enabled/default ]]; then
    sudo rm -f /etc/nginx/sites-enabled/default
  fi
  sudo nginx -t
  sudo systemctl daemon-reload
  sudo systemctl enable mariadb nginx tonghong-backend tonghong-mrp tonghong-frontend
  echo "Unit systemd terpasang. Jalankan: $0 start"
}

usage() {
  echo "Usage: $0 {start|stop|restart|status|logs|install}" >&2
  exit 1
}

case "${1:-}" in
  start) cmd_start ;;
  stop) cmd_stop ;;
  restart) cmd_restart ;;
  status) cmd_status ;;
  logs) cmd_logs ;;
  install) cmd_install ;;
  *) usage ;;
esac
