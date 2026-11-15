# slugs-shell: SSH access to the SLUGS website

Recovered from the original setup archive and checked against the running service on 15 November 2026. This documents the shell container, independently of the visual editor. No live service is replaced by checking out this source or running its local integration test.

## Architecture and connections

```mermaid
flowchart LR
  Client[Authorised SSH or SFTP client] -->|Internet TCP 2234| Router[Router / NAS firewall]
  Router -->|NAS 192.168.1.99:2234| SSH[slugs-shell container :2222]
  SSH -->|uid 1026 gid 100 RW| Site[/volume1/web/slugs]
  SSH --> Identity[slugs-shell-hostkeys volume]
```

| Setting | Value |
| --- | --- |
| Public hostname | `granvillehouse.synology.me` |
| Public/NAS port | `2234` |
| Username | `slugs` |
| Container | `slugs-shell` |
| Original active image | `slugs-shell:2` (rebuild script uses a new dated image tag) |
| Container SSH port | `2222` |
| NAS bind IP in original launch | `192.168.1.99` |
| Website mount | `/volume1/web/slugs:/volume1/web/slugs:rw` |
| Private host identity | Docker volume `slugs-shell-hostkeys` → `/hostkeys` |
| Docker network | `slugs-shell-net` |
| Identity inside container | UID 1026, GID 100 (`users`), Bash shell |

This is a full Unix shell **inside an isolated container**, not a shell on DSM itself. It can read the container's own operating-system files and use its installed tools; the website is the only intended NAS directory mounted. It can modify every website file its UID/GID/ACL permits. It has network access; this is not an outbound network sandbox. It cannot administer NAS containers because no Docker socket is mounted. Keep administrative SSH separate.

## Runtime protections

OpenSSH permits only `slugs`, using public keys. Password, keyboard-interactive and root login are disabled. TCP/agent/X11 forwarding and user RC/environment hooks are disabled; interactive terminals and internal SFTP are enabled. The root filesystem is read-only. `/run`, `/tmp` and the user's home are temporary; do not store persistent work there. The website and host-key volume persist.

The daemon starts as root to handle SSH authentication and drops sessions to `slugs`. Its launch grants only SETUID, SETGID, SYS_CHROOT, CHOWN and FOWNER capabilities, with no-new-privileges, memory/log limits and a requested PID limit. Some Synology kernels do not support enforcement of the PID limit. This is not a privileged container.

## New-computer setup

Generate the key on the connecting computer so its private half stays there:

```sh
ssh-keygen -t ed25519 -f ~/.ssh/slugs_nas
ssh -p 2234 -i ~/.ssh/slugs_nas slugs@granvillehouse.synology.me
sftp -P 2234 -i ~/.ssh/slugs_nas slugs@granvillehouse.synology.me
```

Choose a key passphrase if desired; SSH does not require an account password. Give only the `.pub` file to the NAS administrator. Verify the host fingerprint privately with the administrator before accepting the first connection. Never disable host-key checking to hide an unexpected identity change.

## First installation / key management

On the NAS, place this folder outside the public web root. Supply `authorized_keys` privately with one approved public key per line; it is Git-ignored. Build `slugs-shell:2`, then launch from an administrator session:

```sh
cd /volume1/docker/sluggyslug-source/shell
sudo docker build -t slugs-shell:2 .
sudo sh deploy.sh
sudo sh test-running.sh
```

The first build needs that nonempty `authorized_keys` file. `deploy.sh` refuses to replace an existing container. It creates the dedicated network and host-key volume and uses `NAS_BIND_IP=192.168.1.99` unless overridden, for example `sudo NAS_BIND_IP=192.168.1.99 sh deploy.sh`. Confirm the website UID/GID/ACL and NAS IP first; do not recursively loosen permissions. Configure router/firewall TCP 2234 forwarding to this NAS separately. No HTTPS reverse proxy or editor account is involved.

Host keys are generated only when absent. Preserve the volume across rebuilds to avoid changing the server fingerprint. Public client keys are currently copied into the image at build time. To add/revoke access, prepare a private authorised-key file with the intended complete list and build a new image using it, then replace the container. The normal `rebuild.sh` deliberately snapshots the current container's list; it does not add/revoke keys from a stale file in Git. Removing a key prevents new logins; review existing sessions separately when revoking access. Public-key lists and account names can reveal access membership, so the list is not committed here.

## Rebuild the existing service

Keep a separate DSM administrator SSH session open. Do not run replacement from the `slugs` session that you are replacing. Update Git first, completing any interactive authentication before pasting more commands.

```sh
git -C /volume1/docker/sluggyslug-source pull --ff-only
```

Then run a build-only check (does not stop the service):

```sh
cd /volume1/docker/sluggyslug-source
sudo sh shell/rebuild.sh --build-only
```

After review, rebuild and apply:

```sh
sudo sh shell/rebuild.sh --apply
```

The script verifies the expected persistent mounts and port, preserves the current authorised public keys in a temporary build context, builds a dated image, and retains the previous container under `slugs-shell-rollback-TIMESTAMP`. It preserves the detected NAS bind IP and host-key volume. Replacement briefly interrupts shell access. A failure of launch/read-only checks triggers restoration of the previous container. Read-only checks do not prove internet/router reachability; test that separately. The temporary context is removed on exit. No account password, private client key or host private key is copied into Git or the build context.

This recreates the recovered launch configuration, not arbitrary undocumented custom changes. Before applying on a changed installation, review `sudo docker inspect slugs-shell` privately and compare networking, extra mounts and resource settings. Keep the inspection output out of Git. The script stops before replacement if expected mount/port checks fail. Retain a private backup of the full host-key volume and the website before maintenance.

## Test harness

Read-only checks against the real NAS container, from an administrator session:

```sh
sudo sh shell/test-running.sh
```

Local integration test on a computer with Docker, Python 3, OpenSSH client and ssh-keygen:

```sh
python3 tests/test_shell_integration.py
```

The integration harness builds a disposable image with a generated test client key, publishes a random loopback port, uses temporary site/host-key storage, verifies key login, UID, website read/write/execute, read-only OS protection, denied unapproved key and SSH authentication/forwarding policy. It pins the known-host entry to the test server public key. It cleans up only its uniquely named container/image and temporary files. It never connects to or writes the NAS. Normal unittest discovery does not run this Docker test implicitly.

Internet acceptance from an authorised computer:

```sh
ssh -o BatchMode=yes -p 2234 -i /path/to/private-key slugs@granvillehouse.synology.me 'id; test -r /volume1/web/slugs && test -w /volume1/web/slugs && test -x /volume1/web/slugs'
sftp -P 2234 -i /path/to/private-key slugs@granvillehouse.synology.me
```

Check the fingerprint is unchanged, SSH commands work and SFTP lists the website. For an explicit production write/upload check, use a clearly named disposable file under `new` and remove only that test file afterward. Do not overwrite historical files. Keep current keys and test results private where appropriate.

## Rollback and recovery

If an applied version fails later, find the retained rollback name with `sudo docker ps -a --filter name=slugs-shell`. From the administrator session, stop and rename the failed current container, rename the chosen rollback container to `slugs-shell`, then start it. Do not delete the website or host-key volume. Verify fingerprint/login afterward. Keep failed and rollback containers until recovery is confirmed; cleaning them is a separate decision.

If all containers/images are lost, restore the host-key volume and website from private NAS backups, restore the approved public-key list, rebuild and launch. Without the original host keys the server identity changes; confirm and distribute the new fingerprint rather than bypassing checks. User private keys cannot be recovered from this repository; their owners must supply approved replacement public keys if lost.

## Package

```sh
python3 scripts/package-shell.py
```

Produces `dist/slugs-shell-container.zip` with source, rebuild/deploy/read-only checks, documentation and local integration harness. It deliberately omits `authorized_keys`, private keys and runtime data. Supply keys privately for a fresh installation, or use the current-container rebuild flow to preserve them.

## Validation record — 15 November 2026

- Read-only SSH inspection of the live service confirmed Alpine 3.23.8, UID 1026/GID 100, the recovered sshd policy/entrypoint and expected website/host-key mounts. No live rebuild or website write was performed.
- Disposable Docker integration test passed: image build, approved-key login, UID, site read/write/execute, OS write protection/no Docker socket, SSH policy and rejection of an unapproved key. The temporary container/image were removed by the harness.
- Shell syntax checks, package generation and the nine existing editor/repository tests passed.
- NAS-administrator `test-running.sh`, live replacement/automatic rollback and fresh internet SFTP acceptance are supplied for the next maintenance window; they have not been exercised by this change. They require administrator access or a client key as documented.
