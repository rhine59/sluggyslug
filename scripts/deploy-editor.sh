#!/bin/sh
# Run on the NAS after reviewing DEPLOYMENT.md and the read/write bind mount.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname "$script_dir")
if [ "${1:-}" != "--start" ]; then
  echo 'Review editor/docker-compose.yml and docs/DEPLOYMENT.md first.'
  echo 'Then run scripts/deploy-editor.sh --start on the NAS.'
  exit 2
fi
[ -d /volume1/web/slugs ] || { echo 'Expected NAS website root is missing'; exit 1; }
cd "$repo_dir/editor"
docker compose -f docker-compose.yml config --quiet
docker compose -f docker-compose.yml up -d --build --force-recreate
docker compose -f docker-compose.yml ps
