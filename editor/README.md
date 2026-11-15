# SLUGS editor

Visual page editing with VvvebJs, plus a Flask/Waitress service for individual logins, uploads, permissions, backups and conflict detection. Built for the existing SLUGS HTML archive; no database migration of the website is required.

## Container

Name: slugs-editor
Website mount: /volume1/web/slugs -> /site, read/write
Private account and backup storage: Docker volume slugs-editor-data -> /data
Process: unprivileged UID 1026, GID 100; no Docker socket or privileged mode
Backend listener: NAS loopback 127.0.0.1:8097 (HTTP, behind HTTPS reverse proxy)
Build: docker compose -f docker-compose.yml up -d --build

Expose the editor through a trusted HTTPS reverse proxy. COOKIE_SECURE=1 is required for production; no public HTTP login. Keep the backend port on loopback. TRUST_PROXY=1 is appropriate only behind the NAS proxy.

## First use

The administrator retrieves the one-time code with:

docker exec slugs-editor cat /data/setup-token

Visit /setup over the editor's HTTPS URL, enter that code, and choose a username and a password of at least 14 characters. There is no default password. Setup becomes unavailable after the first account is created. Keep the setup code private.

## Editing

Sign in, choose a folder, then choose Edit visually for an HTML page. Click/double-click text or images to edit them. Use Save to publish. Page scripts are disabled inside the editor's preview; open the public website to check interactive galleries. Source opens a text editor for HTML, CSS, JavaScript and other text files.

Files & uploads lets you upload images, PDFs, Office documents, ZIP files, audio and video into your chosen website folder. The general uploader accepts up to 100 MB per file. The visual builder's image uploader accepts up to 20 MB. HEIC and SVG uploads are not supported; use JPEG, PNG or WebP for photographs. Executables/server scripts are not accepted by the uploader. Replacing an existing file requires confirmation and retains a backup.

Use Copy link to obtain a public website link for an uploaded file. Inside the visual builder, select an image and Set image to upload/choose an image. Use the link property or text link control to link to a document.

## Accounts

Administrators can create individual editor or administrator accounts. A permitted folder of new restricts edits to /new; a blank permitted folder allows editing the entire mounted web root. Users are not Synology system accounts. Disabling an account or changing its permissions/password ends its existing sessions. An administrator cannot disable their own account through the account-management API; another administrator must do that.

## Recovery

History shows earlier versions for a file. Restoring also backs up the current version. Concurrent saves require the current file hash; a changed file is rejected rather than overwritten. Activity records who saved, uploaded or restored content. Backups are outside the public web root. Back up the slugs-editor-data Docker volume regularly: it holds users, session keys and revision history. Website backups remain necessary; this editor's history only covers changes made through the editor.

## Maintenance

Application source, Dockerfile, dependency versions and the VvvebJs licence are included. Keep this source folder, the web root and the private data volume when updating. Review dependency updates regularly. No files in the existing site are changed merely by starting the container.
