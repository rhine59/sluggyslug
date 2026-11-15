#!/bin/sh
# Default: build only. --apply replaces the running SSH service with rollback.
set -eu
app_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mode=${1:---build-only}
case "$mode" in --build-only|--apply) ;; *) echo 'Usage: rebuild.sh [--build-only|--apply]'; exit 2;; esac
D=${DOCKER:-docker}
"$D" inspect slugs-shell >/dev/null
# Keep host identity and site storage; reject an unexpected layout.
[ "$("$D" inspect -f '{{range .Mounts}}{{if eq .Destination "/hostkeys"}}{{.Name}}{{end}}{{end}}' slugs-shell)" = slugs-shell-hostkeys ] || { echo 'Unexpected host-key mount; review manually.'; exit 1; }
[ "$("$D" inspect -f '{{range .Mounts}}{{if eq .Destination "/volume1/web/slugs"}}{{.Source}}{{end}}{{end}}' slugs-shell)" = /volume1/web/slugs ] || { echo 'Unexpected website mount; review manually.'; exit 1; }
NAS_BIND_IP=$("$D" inspect -f '{{(index (index .HostConfig.PortBindings "2222/tcp") 0).HostIp}}' slugs-shell)
port=$("$D" inspect -f '{{(index (index .HostConfig.PortBindings "2222/tcp") 0).HostPort}}' slugs-shell)
[ "$port" = 2234 ] && [ -n "$NAS_BIND_IP" ] && [ "$NAS_BIND_IP" != 0.0.0.0 ] || { echo 'Unexpected port binding; review manually.'; exit 1; }
export NAS_BIND_IP
ctx=$(mktemp -d)
trap 'rm -rf "$ctx"' EXIT HUP INT TERM
cp "$app_dir/Dockerfile" "$app_dir/sshd_config" "$app_dir/entrypoint.sh" "$app_dir/.dockerignore" "$ctx/"
# Preserve every currently installed public key, not the old archive copy.
"$D" cp slugs-shell:/etc/ssh/slugs_authorized_keys "$ctx/authorized_keys"
[ -s "$ctx/authorized_keys" ] || { echo 'Authorised keys are missing; refusing rebuild.'; exit 1; }
IMAGE="slugs-shell:rebuild-$(date +%Y%m%d%H%M%S)"
export IMAGE
"$D" build --pull -t "$IMAGE" "$ctx"
printf 'Built %s. Current service is unchanged.\n' "$IMAGE"
[ "$mode" = --apply ] || exit 0
# Use a separate administrator session; the slugs SSH session will disconnect.
old="slugs-shell-rollback-$(date +%Y%m%d%H%M%S)"
"$D" stop slugs-shell
"$D" rename slugs-shell "$old"
if DOCKER="$D" sh "$app_dir/deploy.sh" && DOCKER="$D" sh "$app_dir/test-running.sh"; then
 printf 'Replacement passed checks. Retained stopped rollback container: %s\n' "$old"
else
 echo 'Replacement failed; restoring previous container.' >&2
 "$D" rm -f slugs-shell >/dev/null 2>&1 || true
 "$D" rename "$old" slugs-shell
 "$D" start slugs-shell
 exit 1
fi
