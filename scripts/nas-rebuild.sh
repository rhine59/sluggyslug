#!/bin/sh
# Run on the NAS against an extracted editor package or a repository checkout.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname "$script_dir")
app_dir=${1:-"$repo_dir/editor"}
[ -f "$app_dir/Dockerfile" ] && [ -f "$app_dir/docker-compose.yml" ] || { echo 'Supply the directory containing Dockerfile and docker-compose.yml.'; exit 2; }
[ -d /volume1/web/slugs ] || { echo 'Run on the NAS with /volume1/web/slugs available.'; exit 2; }
cd "$app_dir"
docker compose -f docker-compose.yml config --quiet
# Explicit tag/build/recreation avoids accidentally restarting an old image.
docker build --pull --no-cache -t slugs-editor:1.0 .
docker compose -f docker-compose.yml up -d --no-build --force-recreate slugs-editor
docker compose -f docker-compose.yml ps
printf '%s\n' 'Run scripts/test-deployment.py against the HTTPS address, then scripts/editor-setup.sh.'
