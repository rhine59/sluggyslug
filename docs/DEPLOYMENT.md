# Deploy or rebuild on Synology

## Prerequisites

- Synology Container Manager / Docker Compose.
- Website document root verified as `/volume1/web/slugs`.
- UID 1026/GID 100 must have access to that directory. Adjust `USER` in the Dockerfile if deploying on a different NAS; do not broadly relax NAS permissions.
- HTTPS reverse proxy for the editor, with a certificate valid for its hostname. The suggested hostname is `slugs-editor.granvillehouse.synology.me`; DNS was found to resolve, but certificate/proxy configuration is not yet verified complete.
- Check that host loopback port 9087 is free.

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

The service binds only to NAS loopback `127.0.0.1:9087`. Configure the NAS HTTPS reverse proxy to send the editor hostname to `http://127.0.0.1:9087`. Keep `COOKIE_SECURE=1` and `TRUST_PROXY=1`; the backend must remain reachable only through that trusted proxy. Do not forward port 9087 on the router or expose an unauthenticated demo editor.

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
