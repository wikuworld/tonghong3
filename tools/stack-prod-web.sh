#!/usr/bin/env bash
# Kembali ke frontend production (build statis nginx) di WEB_PORT.
# Usage: ./tools/stack-prod-web.sh [--build]
set -euo pipefail
cd "$(dirname "$0")/.."

BUILD=""
if [[ "${1:-}" == "--build" ]]; then
  BUILD="--build"
fi

echo "==> Stop stack HMR (profile dev)..."
docker compose --profile dev stop web-hmr frontend-dev backend-dev 2>/dev/null || true

echo "==> Start build statis (web) + backend..."
if [[ -n "$BUILD" ]]; then
  docker compose build web
fi
docker compose up -d mariadb backend web

docker compose ps web backend
echo ""
echo "Production statis aktif di port ${WEB_PORT:-8080}"
echo "Untuk HMR lagi: ./tools/stack-hmr-domain.sh"
