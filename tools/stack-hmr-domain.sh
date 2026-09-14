#!/usr/bin/env bash
# Aktifkan Vite HMR di port origin Cloudflare (default 8080) — domain tetap sama.
# Usage: ./tools/stack-hmr-domain.sh
set -euo pipefail
cd "$(dirname "$0")/.."

WEB_PORT="${WEB_PORT:-8080}"
WEB_HMR_PORT="${WEB_HMR_PORT:-8080}"
export WEB_HMR_PORT

if [[ "$WEB_HMR_PORT" != "$WEB_PORT" ]]; then
  echo "Peringatan: WEB_HMR_PORT=$WEB_HMR_PORT ≠ WEB_PORT=$WEB_PORT"
  echo "Cloudflare origin biasanya ke $WEB_PORT — set WEB_HMR_PORT=$WEB_PORT di .env"
fi

echo "==> Stop build statis (web) agar port $WEB_HMR_PORT bebas untuk HMR..."
docker compose stop web 2>/dev/null || true

echo "==> Pastikan backend + mariadb jalan (restart backend agar route API terbaru ter-load)..."
docker compose up -d mariadb backend
docker compose restart backend

echo "==> Start Vite HMR + nginx proxy (profile dev)..."
docker compose --profile dev up -d frontend-dev web-hmr

echo "==> Menunggu Vite siap (bisa 2–5 menit pertama kali npm install)..."
deadline=$((SECONDS + 360))
while (( SECONDS < deadline )); do
  if docker compose --profile dev ps frontend-dev 2>/dev/null | grep -q healthy; then
    break
  fi
  sleep 5
  echo "   ... masih menunggu frontend-dev"
done

if ! docker compose --profile dev ps frontend-dev 2>/dev/null | grep -q healthy; then
  echo "frontend-dev belum healthy. Cek log: docker compose --profile dev logs frontend-dev --tail 80"
  exit 1
fi

docker compose --profile dev ps web-hmr frontend-dev
echo ""
echo "HMR aktif di port $WEB_HMR_PORT"
echo "Buka: https://${HMR_PUBLIC_HOST:-tonghong.creativedigitalsolutions.id}"
echo "Kembali ke build statis: ./tools/stack-prod-web.sh"
