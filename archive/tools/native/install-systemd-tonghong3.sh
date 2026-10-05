#!/usr/bin/env bash
# Alias lama: unit UAT sekarang bernama tonghong-uat-*.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec "$ROOT/tools/native/install-systemd-tonghong-uat.sh" "$@"
