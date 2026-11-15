# Complete rebuild, setup and test procedure

Production: https://slugs-editor.granvillehouse.synology.me/  
NAS service: `slugs-editor`, loopback port **8097**, container port **8080**.  
Website: `/volume1/web/slugs`; private accounts/history: `slugs-editor-data`.

## 1. Recover or prepare the source

Clone the private repository on a computer with GitHub access:

```sh
git clone https://github.com/rhine59/sluggyslug.git
cd sluggyslug
python3 -m venv .venv
.venv/bin/pip install -r editor/requirements.txt
PYTHON=.venv/bin/python sh scripts/test.sh
```

This runs backend/repository tests, builds the editor ZIP under `dist`, and checks the website snapshots. It does not deploy or change the live NAS. Docker builds use the dependencies pinned in `editor/requirements.txt`; the upstream Python base image is updated when pulled, so rebuilds are not bit-for-bit reproducible. Vendored visual-editor files and licences are included.

## 2. Back up before deployment

Use your existing NAS backup process to preserve both `/volume1/web/slugs` and the Docker volume `slugs-editor-data`. The latter contains account records, session keys and revision history. Keep backups private and outside the public web root. Git cannot replace these backups. Never delete the data volume as a rebuild step.

For disaster recovery, restore the website and private data volume before launching the container. Restored accounts remain usable; restoring only source does not restore accounts/history. Review source/image compatibility before restoring an older application version against newer private data.

## 3. Transfer and rebuild the editor

Either clone the repository on the NAS, or extract `dist/slugs-editor-container.zip` into `/volume1/docker/slugs-editor`. Preserve existing site/data mounts. Check the Compose file uses `127.0.0.1:8097:8080` and the intended full read/write website mount.

From a repository checkout on the NAS:

```sh
sudo sh scripts/nas-rebuild.sh
```

To rebuild an extracted package using the helper from a checkout:

```sh
sudo sh scripts/nas-rebuild.sh /volume1/docker/slugs-editor
```

Without a checkout, run these equivalent commands in the extracted package:

```sh
cd /volume1/docker/slugs-editor
sudo docker compose -f docker-compose.yml config --quiet
sudo docker build --pull --no-cache -t slugs-editor:1.0 .
sudo docker compose -f docker-compose.yml up -d --no-build --force-recreate slugs-editor
sudo docker ps --filter name=slugs-editor
sudo docker exec slugs-editor tail -n 3 /app/app.py
```

The running code must include `clear_untrusted_proxy_headers=False`. A successful build alone does not prove the old container was replaced. If a rebuild fails, inspect its output before changing or removing anything. Existing website traffic is served separately by Web Station.

## 4. Configure public HTTPS

In DSM Login Portal → Advanced → Reverse Proxy, use:

| Setting | Value |
| --- | --- |
| Source | HTTPS, `slugs-editor.granvillehouse.synology.me`, port 443 |
| Destination | HTTP, `127.0.0.1`, port 8097 |
| Request header `X-Forwarded-Proto` | `https` |
| Request header `X-Forwarded-Host` | `slugs-editor.granvillehouse.synology.me` |

Assign the certificate valid for that hostname to this service in Security → Certificate → Settings. DNS must point to your NAS internet connection and public HTTPS traffic must reach NAS port 443. Do not expose port 8097 publicly. Keep `COOKIE_SECURE=1`, `TRUST_PROXY=1`, and the loopback binding. Waitress preserves the proxy headers for ProxyFix; Origin/CSRF checks remain enabled.

## 5. Initialise accounts privately

From the repository checkout on the NAS:

```sh
sudo sh scripts/editor-setup.sh
```

Or, for an extracted package:

```sh
sudo docker exec slugs-editor cat /data/setup-token
```

Enter the code at `/setup`, choose an individual administrator username and password of at least 14 characters, and submit in your browser. Do not put these values in Git, shell command arguments or logs. Setup is unavailable after the first account exists. Sign out and sign back in. Use User accounts to create individual editors limited to `new`; a blank permitted folder grants the whole website root. Keep a second trusted administrator for recovery. Account resets are described in USER-ACCESS.md.

## 6. Run checks

From any computer with Python 3 and internet access:

```sh
python3 scripts/test-deployment.py
```

The script verifies HTTPS certificate validation, healthy response, denial of unauthenticated file access, and availability of the home/sign-in/setup page. It is read-only and requires no password. Run `scripts/test.sh` again when changing application source.

Complete these manual checks using a disposable folder inside `new`:

1. Sign in as administrator; create a test page, visually edit text, save, and check it on the public website.
2. Upload a test photograph and PDF; insert/link them and verify their public URLs.
3. Edit twice; use History to restore an earlier revision.
4. Open a page in two tabs; after saving one, ensure the stale save in the other is rejected.
5. Create an editor restricted to `new`; confirm root files and User accounts are inaccessible.
6. Disable that editor; confirm their existing session stops working.
7. Confirm `/setup` is unavailable after initialisation.

Do not use historical pages for acceptance tests. Remove only your clearly identified disposable test content through an authorised file-management process after testing. Record date/results in STATUS.md, distinguishing automated checks, owner confirmations and independently observed results.

## Website rebuild and photos

```sh
python3 scripts/restore-media.py --ssh slugs-nas
python3 scripts/rebuild-site.py --output dist/webroot
python3 scripts/check-site.py
```

The SSH alias must be configured with an authorised key (see USER-ACCESS.md). Bulk photographs remain excluded from Git. For a source-only package, skip media restoration and use `rebuild-site.py --code-only`. Preserve existing NAS photographs when transferring a partial build. Do not use a deletion-based sync for that transfer. A repository snapshot can predate live editor changes: review differences and back up before publishing it. Website rebuild scripts stage local output; they do not automatically overwrite the NAS.

## Troubleshooting

- Port conflict: preserve the existing unrelated service; verify both Compose and reverse proxy use 8097.
- Page not found: compare source hostname, HTTPS port, backend port and certificate assignment.
- Origin mismatch: verify both forwarded request headers and `TRUST_PROXY=1`; inspect the running `/app/app.py`, not just the NAS source file.
- Old code after build: use the explicit image build and forced recreation above.
- DSM says container `undefined`: refresh Container Manager and check `sudo docker ps -a --filter name=slugs-editor` over SSH.
- Lost accounts/history: check the correct persistent data volume is attached before attempting setup again. Never delete the volume to reset a login.
