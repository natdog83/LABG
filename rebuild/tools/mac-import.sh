#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
import_mode=''
if [[ ${1:-} == '--refresh' && $# == 1 ]]; then
    import_mode=refresh
elif [[ $# != 0 ]]; then
    echo 'Usage: bash rebuild/tools/mac-import.sh [--refresh]'
    echo '--refresh deliberately replaces previously recovered pages with the archived content.'
    exit 1
fi
docker compose run --rm cli core is-installed || { echo 'Complete WordPress setup at http://localhost:8080/ first.'; exit 1; }
docker compose run --rm cli theme activate labg-recovery
if [[ "$import_mode" == refresh ]]; then
    docker compose run --rm cli eval-file /rebuild/wordpress/import.php refresh
else
    docker compose run --rm cli eval-file /rebuild/wordpress/import.php
fi
printf '\nRecovered site: http://localhost:8080/\nWordPress admin: http://localhost:8080/wp-admin/\n'
