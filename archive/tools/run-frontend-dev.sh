#!/usr/bin/env bash
# Jalankan Vite HMR untuk systemd (nvm + env native).
set -euo pipefail
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
# shellcheck disable=SC1091
. "$NVM_DIR/nvm.sh"
nvm use 22 >/dev/null
cd /home/developer/project/frontend
export VITE_API_PROXY="${VITE_API_PROXY:-http://127.0.0.1:8000}"
export WEB_PORT="${WEB_PORT:-8080}"
export VITE_HMR_PROTOCOL="${VITE_HMR_PROTOCOL:-ws}"
export VITE_HMR_PORT="${VITE_HMR_PORT:-5173}"
export VITE_HMR_CLIENT_PORT="${VITE_HMR_CLIENT_PORT:-${WEB_PORT}}"
exec npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
