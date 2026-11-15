#!/bin/sh
# Read-only checks, run as NAS administrator; no website writes or key output.
set -eu
D=${DOCKER:-docker}
[ "$("$D" inspect -f '{{.State.Running}}' slugs-shell)" = true ]
[ "$("$D" inspect -f '{{.HostConfig.ReadonlyRootfs}}' slugs-shell)" = true ]
"$D" exec slugs-shell /usr/sbin/sshd -t
policy=$("$D" exec slugs-shell /usr/sbin/sshd -T)
for setting in 'passwordauthentication no' 'kbdinteractiveauthentication no' 'permitrootlogin no' 'pubkeyauthentication yes' 'authenticationmethods publickey' 'disableforwarding yes' 'allowusers slugs'; do
 printf '%s\n' "$policy" | grep -Fx "$setting" >/dev/null || { echo "FAIL: $setting"; exit 1; }
done
[ "$("$D" exec slugs-shell id -u slugs)" = 1026 ]
[ "$("$D" exec slugs-shell id -g slugs)" = 100 ]
"$D" exec -u slugs slugs-shell sh -c 'test -r /volume1/web/slugs && test -w /volume1/web/slugs && test -x /volume1/web/slugs && test ! -w /etc/passwd'
"$D" exec slugs-shell test -s /etc/ssh/slugs_authorized_keys
"$D" exec slugs-shell test -s /hostkeys/ssh_host_ed25519_key
"$D" port slugs-shell 2222/tcp
printf '%s\n' 'PASS: running, read-only root, SSH policy, uid/gid, directory access and persistent key files.' 'Also test SSH/SFTP from another computer and verify host fingerprint continuity.'
