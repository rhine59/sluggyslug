#!/bin/sh
# Build only. Starting a NAS service is a separate, explicit operation.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname "$script_dir")
cd "$repo_dir/editor"
docker compose -f docker-compose.yml config --quiet
docker compose -f docker-compose.yml build
