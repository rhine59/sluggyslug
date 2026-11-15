#!/bin/sh
# Run privately on the NAS; never redirect this output into logs or Git.
set -eu
container_name=${1:-slugs-editor}
printf '%s\n' 'Open https://slugs-editor.granvillehouse.synology.me/setup' 'If setup is already complete, use the sign-in page instead.' 'Private setup code follows. Do not share it or save it in Git:'
docker exec "$container_name" cat /data/setup-token
printf '\n%s\n' 'Choose your administrator username and password in the browser.' 'After signing in, create separate editor accounts with permitted folder new.'
