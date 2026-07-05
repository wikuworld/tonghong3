#!/usr/bin/env bash
# Muat nvm ke PATH shell saat ini (agen Cursor / shell non-login).
# Pakai dari root repo:
#   source tools/nvm-load.sh
#   cd frontend && npm run lint
#
# Jangan dijalankan sebagai ./nvm-load.sh — harus di-source agar PATH berlaku di shell induk.

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ -s "$NVM_DIR/nvm.sh" ]; then
  # shellcheck disable=SC1091
  . "$NVM_DIR/nvm.sh"
elif [ -s "/usr/local/opt/nvm/nvm.sh" ]; then
  # shellcheck disable=SC1091
  . "/usr/local/opt/nvm/nvm.sh"
elif [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then
  # shellcheck disable=SC1091
  . "/opt/homebrew/opt/nvm/nvm.sh"
fi
