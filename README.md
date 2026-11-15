# SLUGS website and editor

Source, assets and rebuild tools for the Society of Lancaster University Graduate Speleologists archive and its containerised visual editor.

| Folder | Contents |
| --- | --- |
| `website/original/` | Preserved original pages, documents, galleries and supporting assets; bulk photographs remain on the NAS |
| `website/new/` | Reorganised pages, repaired links, chronological events list, reports and small layout assets |
| `editor/` | `slugs-editor` application, vendored VvvebJs visual builder, Dockerfile and Compose configuration |
| `tests/` | Account, permission, upload, backup, restore, conflict and site-integrity checks |
| `scripts/` | Rebuild, packaging, testing and deployment helpers |
| `docs/` | Architecture, installation, security, editing and operational notes |
| `reports/` | Link-repair report, detailed results and snapshot manifests |
| `tools/archive-migration/` | Historical migration/audit code, retained for reference |

For addresses, account names and login instructions, see [User access](docs/USER-ACCESS.md).

See [current status](docs/STATUS.md) before deploying. The owner has confirmed the NAS container healthy and HTTPS/account setup working; remaining acceptance checks are listed in the status document.

## Rebuild the website

```sh
python3 scripts/restore-media.py --ssh slugs-nas  # optional: fetch the Git-excluded photos
python3 scripts/rebuild-site.py --output dist/webroot
python3 scripts/check-site.py
```

The photo library is deliberately excluded from Git. Its paths and hashes are recorded in `reports/nas-media-manifest.json`; restore it from the existing NAS for a complete offline rebuild. Use `--code-only` to stage pages and supporting assets without downloading photographs, and preserve existing media when deploying that partial build.

The resulting complete document root contains the original site at its root and the new site in `new/`. Rebuilding does not upload anything or alter the NAS. The checked-in website snapshots are authoritative; historical migration tools must not overwrite subsequent editor changes.

## Test and build the editor

```sh
python3 -m venv .venv
.venv/bin/pip install -r editor/requirements.txt
.venv/bin/python -m unittest discover -s tests -p 'test_editor.py' -v
python3 scripts/package-editor.py --output dist/slugs-editor-container.zip
./scripts/rebuild-editor.sh
```

[Full rebuild, setup and tests](docs/REBUILD-SETUP-TEST.md) · [Deploy on Synology](docs/DEPLOYMENT.md) · [Architecture](docs/ARCHITECTURE.md) · [Editor guide](docs/EDITOR.md) · [Test harness](docs/TESTING.md) · [Security and recovery](docs/SECURITY.md)

Credentials, SSH keys, account databases and private revision backups are not part of this repository. Website photographs and documents retain their existing contributor copyright notices; no blanket licence is assigned to the archive. Third-party editor licences are included alongside their code.
