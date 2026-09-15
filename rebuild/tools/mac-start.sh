#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null 2>&1 || { echo 'Install Docker Desktop for your Mac: https://docs.docker.com/desktop/setup/install/mac-install/'; exit 1; }
docker compose version >/dev/null 2>&1 || { echo 'Docker Compose is required; update Docker Desktop.'; exit 1; }
docker info >/dev/null 2>&1 || { echo 'Open Docker Desktop, wait for it to start, and run this command again.'; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo 'Python 3 is required for setup and recovery tools.'; exit 1; }
[[ -s generated/pages.json && -d generated/assets ]] || { echo 'Extract LABG-public-capture-2026-09-15.tar.gz at the LABG repository root first. It must populate rebuild/generated and rebuild/archive.'; exit 1; }
python3 - <<'PY'
import os,secrets
if not os.path.exists('.env'):
    with os.fdopen(os.open('.env',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:
        f.write('DB_PASSWORD='+secrets.token_hex(24)+'\nDB_ROOT_PASSWORD='+secrets.token_hex(24)+'\n')
    print('Created local database settings.')
PY
docker compose up -d --build wordpress
printf '\nOpen http://localhost:8080/ and complete the WordPress setup.\nThen run: bash rebuild/tools/mac-import.sh (from the repository root).\n'
