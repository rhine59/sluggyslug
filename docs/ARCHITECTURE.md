# Architecture

## Existing public site

Web Station continues to serve `/volume1/web/slugs`. The original archive is at the root; the reorganised archive is under `/new`. Starting the editor does not change the original pages, Web Station's static-site configuration or the public site's routing.

## Editor

```mermaid
flowchart LR
  Browser[Author's browser] -->|HTTPS| Proxy[Synology HTTPS reverse proxy]
  Proxy -->|Loopback HTTP :9087| App[slugs-editor: Waitress + Flask]
  App -->|Read / write| Website[/volume1/web/slugs mounted at /site]
  App -->|Accounts, sessions, audit| DB[(Private SQLite database)]
  App -->|Prior file versions| Backup[Private revision storage]
  Browser --> Builder[VvvebJs visual builder]
  Builder -->|Authenticated read / save / upload| App
```

The container runs as UID 1026/GID 100. Its filesystem is read-only except for the website mount, the private data volume and a temporary filesystem. All Linux capabilities are dropped. It has no Docker socket, privileged mode or access to the rest of the NAS.

The website bind mount is intentionally read/write for the **entire** web root, as requested. Application permissions determine which users may modify which folders. The first administrator has full web-root access. Additional editors default to the `new` folder; an administrator may choose another folder or the whole root.

### Editing flow

1. An authenticated author selects an HTML page. The server returns its contents, encoding and SHA-256 version.
2. VvvebJs loads the actual page through an authenticated preview route. Browser sandboxing disables the page's scripts, forms and nested frames while retaining same-origin DOM access for the parent editor.
3. The author changes text, images, links, components or layout. The source editor is also available for text files.
4. Save submits the full HTML with the version opened by the author.
5. The server locks that path, checks the version, writes a private backup, then atomically replaces the file. A conflicting save is rejected.
6. The public Web Station site serves the saved file immediately. Interactive behaviour must be checked on the public site because page scripts do not run in the editor preview.

### Storage

- `/site`: bind mount of the existing website. The application only permits resolved, non-hidden paths inside it and rejects symbolic links.
- `/data/editor.sqlite`: users, session records, rate-limit attempts, revision metadata and audit entries.
- `/data/backups/`: previous file bytes, addressed by generated identifiers, not public URLs.
- `/data/locks/`: per-path write locks.
- `/data/session-key`: private cookie signing key.
- `/data/setup-token`: private first-run setup code; setup is unavailable after the first account is created.

The named Docker volume `slugs-editor-data` persists independently of container rebuilds. It is excluded from Git and must be backed up operationally.

### Scope and boundaries

This is a VvvebJs integration with a purpose-built authentication and filesystem service, **not** a migration to Vvveb CMS. Existing HTML files remain the site's content. There is no site-content database and no conversion of the archive to CMS templates.

The preview is a design surface, not a complete browser simulation: script-generated galleries, JavaScript search and forms are checked on the live website. Site authors are trusted to edit website content. This editor does not make their published HTML/JavaScript untrusted or safe for arbitrary anonymous contributors.

## Repository media boundary

The bulk JPEG/TIFF photograph library remains on the NAS. Git stores page files, supporting assets, documents, the editor and a media-path/hash manifest. `scripts/restore-media.py` can populate the ignored photograph paths from a local NAS mount or authorised SSH connection for a complete offline rebuild. This does not remove or alter photographs on the NAS.
