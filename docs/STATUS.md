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

`/volume1/docker/slugs-editor` was created. The updated source package, including the save-control/font fixes and documentation, was uploaded and extracted there on 15 November 2026. The application has not yet been built or started on the NAS.

The NAS Container Manager project was created and its image build was started after launch approval. A running `slugs-editor` container has not yet been verified. HTTPS routing and first-administrator setup remain to be completed. No production editor accounts exist yet. The currently served website was not changed by the editor test; the test used a separate local copy.

## Website history

The repository preserves the original page files and reorganised `/new` copy, supporting assets and documents. The bulk JPEG/TIFF photo library remains on the NAS and is excluded from Git; a media manifest records its paths/hashes and a restore script can retrieve it when required. Link repairs were applied only to `/new`. Subsequent Events changes incorporate 28 external SLUGS Reports blog entries into the chronological list, giving 100 entries at that point.

The November 2026 link check was a dated audit, not continuous monitoring. Reports distinguish successful local checks from unavailable and inconclusive external destinations.

## GitHub workflow access

The runnable tests and an Actions workflow template are included. The template is stored under `ci/` because the current Git credential cannot create files under `.github/workflows/`. No broader GitHub permissions were requested.
