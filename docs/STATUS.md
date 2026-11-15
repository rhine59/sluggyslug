# Delivery and deployment status

Updated 15 November 2026.

## Complete locally

- Container application, Dockerfile and Compose configuration.
- Vendored visual-builder assets and licence.
- Individual administrator/editor accounts with permitted-folder restrictions and account disabling.
- Source editing; folder and HTML-page creation.
- Photo, document, ZIP, audio and video uploads.
- Backup/version history, restore, audit trail and stale-save rejection.
- Seven automated backend test cases passed, covering multiple security and file-operation scenarios.
- Docker image built and run successfully on the Mac against a disposable site copy.
- Browser test confirmed clicking and changing page text, enabling Save, saving it to disk, and retaining a backup. Initial Save-button and missing-font-resource issues were repaired.

## NAS staging

The application is deployed at `/volume1/docker/slugs-editor`, mounting `/volume1/web/slugs` read/write. The owner supplied container output confirming `slugs-editor` running and healthy on NAS loopback **127.0.0.1:8097 → container 8080**.

The HTTPS reverse proxy destination was corrected to port 8097. The owner confirmed certificates sorted and subsequently confirmed editor account setup working. The production administrator's username/password and setup code remain private and are not recorded in Git.

The application now retains forwarded headers at the Waitress boundary so Flask's configured ProxyFix can determine the public HTTPS origin. The reverse proxy supplies `X-Forwarded-Proto: https` and `X-Forwarded-Host: slugs-editor.granvillehouse.synology.me`. The origin/CSRF checks remain enabled. These settings require the backend to stay on loopback behind the trusted NAS proxy.

Production visual-save/upload/restore and restricted-account acceptance checks have not been independently observed; the automated and local browser checks are described above. No production account database, private revision data or credentials are copied into this repository.

## Website history

The repository preserves the original page files and reorganised `/new` copy, supporting assets and documents. The bulk JPEG/TIFF photo library remains on the NAS and is excluded from Git; a media manifest records its paths/hashes and a restore script can retrieve it when required. Link repairs were applied only to `/new`. Subsequent Events changes incorporate 28 external SLUGS Reports blog entries into the chronological list, giving 100 entries at that point.

The November 2026 link check was a dated audit, not continuous monitoring. Reports distinguish successful local checks from unavailable and inconclusive external destinations.

## GitHub workflow access

The runnable tests and an Actions workflow template are included. The template is stored under `ci/` because the current Git credential cannot create files under `.github/workflows/`. No broader GitHub permissions were requested.
