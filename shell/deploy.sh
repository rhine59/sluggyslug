#!/bin/sh
set -eu
D=${DOCKER:-docker}
NAS_BIND_IP=${NAS_BIND_IP:-192.168.1.99}
IMAGE=${IMAGE:-slugs-shell:2}
if "$D" container inspect slugs-shell >/dev/null 2>&1; then
  echo "Refusing to replace an existing slugs-shell container." >&2
  exit 1
fi
"$D" network inspect slugs-shell-net >/dev/null 2>&1 || "$D" network create slugs-shell-net
"$D" volume create slugs-shell-hostkeys
"$D" run -d --name slugs-shell --restart unless-stopped \
 --network slugs-shell-net --read-only \
 --cap-drop ALL --cap-add SETUID --cap-add SETGID --cap-add SYS_CHROOT --cap-add CHOWN --cap-add FOWNER \
 --security-opt no-new-privileges:true \
 --pids-limit 128 --memory 256m --cpu-shares 256 \
 --log-opt max-size=5m --log-opt max-file=2 \
 --tmpfs /run:rw,nosuid,nodev,size=16m \
 --tmpfs /tmp:rw,nosuid,nodev,size=128m,mode=1777 \
 --tmpfs /home/slugs:rw,nosuid,nodev,size=32m,uid=1026,gid=100,mode=700 \
 --mount type=volume,source=slugs-shell-hostkeys,target=/hostkeys \
 --mount type=bind,source=/volume1/web/slugs,target=/volume1/web/slugs \
 -p "$NAS_BIND_IP:2234:2222" "$IMAGE"
