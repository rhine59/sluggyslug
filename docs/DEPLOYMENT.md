# Deploy or rebuild on Synology

## Prerequisites

- Synology Container Manager / Docker Compose.
- Website document root verified as `/volume1/web/slugs`.
- UID 1026/GID 100 must have access to that directory. Adjust `USER` in the Dockerfile if deploying on a different NAS; do not broadly relax NAS permissions.
- HTTPS reverse proxy for the editor, with a certificate valid for its hostname. The production hostname is `slugs-editor.granvillehouse.synology.me`; the owner confirmed HTTPS and account setup working.
- Check that host loopback port 8097 is free.

## Build and run

Place the current `editor/` directory under `/volume1/docker/slugs-editor`, or upload/extract the ZIP produced by `scripts/package-editor.py` there. Check STATUS.md and use the current repository/package version.

From that directory:

```sh
docker compose -f docker-compose.yml config
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up -d
docker compose -f docker-compose.yml ps
```

Container and service name: **slugs-editor**. Website mount: `/volume1/web/slugs:/site:rw`. Private storage: `slugs-editor-data:/data`.

The service binds only to NAS loopback `127.0.0.1:8097`. Configure the NAS HTTPS reverse proxy to send the editor hostname to `http://127.0.0.1:8097`. Keep `COOKIE_SECURE=1` and `TRUST_PROXY=1`; the backend must remain reachable only through that trusted proxy. Do not forward port 8097 on the router or expose an unauthenticated demo editor.

Use a dedicated hostname at `/`, not a subpath: the editor's client endpoints currently use absolute paths. Public website traffic continues through its existing Web Station portal.

## Create the administrator

```sh
docker exec slugs-editor cat /data/setup-token
```

Keep the code private. In your browser, visit `https://YOUR-EDITOR-HOST/setup`, enter the code, and choose a username/password (at least 14 characters). Sign in, then use User accounts to add others with separate logins. Do not put the code, passwords or `/data` contents in Git.

## Verify before handing over

1. `/health` returns `{"status":"ok"}`; unauthenticated `/api/files` returns 401.
2. A valid HTTPS certificate is presented and login cookies are Secure/HttpOnly.
3. Create a disposable page inside `new`, edit visually, save, and view the result through Web Station.
4. Upload a disposable photograph and document, then insert/link them.
5. Check History and restore an earlier version.
6. Open the same test page twice; saving the stale tab must be rejected.
7. Create an editor limited to `new`; confirm it cannot edit root files or manage users.
8. Disable that account and confirm its session ends.

Use test content only; do not overwrite historical pages to perform these checks.

## Updates and rollback

Keep the website and private data volume backed up. Rebuild the image from current source and run Compose up again. Do not remove `slugs-editor-data`. A previous image can be restarted against the same mounts, subject to reviewing schema compatibility if future versions change the database. Website file restoration is available in History; full disaster recovery requires a NAS backup of the web root and the private data volume.

This repository's scripts do not configure certificates, router forwarding or NAS permissions automatically.

## Reverse proxy headers and Origin mismatch

Set the reverse proxy's **request** headers:

| Header | Value |
| --- | --- |
| `X-Forwarded-Proto` | `https` |
| `X-Forwarded-Host` | `slugs-editor.granvillehouse.synology.me` |

Waitress runs with `clear_untrusted_proxy_headers=False` so these headers reach Flask's ProxyFix. Keep `TRUST_PROXY=1` and the loopback-only port binding together. Do not disable the Origin or CSRF checks to work around a proxy problem.

## Rebuild after editing source on the NAS

A source edit does not change the application already copied into an image. From the NAS project directory, explicitly build the named image and recreate the service:

```sh
cd /volume1/docker/slugs-editor
sudo docker build --no-cache -t slugs-editor:1.0 .
sudo docker compose -f docker-compose.yml up -d --no-build --force-recreate slugs-editor
sudo docker exec slugs-editor tail -n 3 /app/app.py
sudo docker ps --filter name=slugs-editor
```

The running file should include `clear_untrusted_proxy_headers=False`, and the published port should be `127.0.0.1:8097->8080/tcp`. Keep the source, private data volume and website mount intact. Port 8091 is already used by another NAS service; do not change that service.
