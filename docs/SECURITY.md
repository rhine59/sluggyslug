# Accounts, access and recovery

- Passwords are hashed using Werkzeug's current default password-hashing method; plaintext passwords are not stored.
- Login sessions have an eight-hour expiry and are checked against the account's current version and enabled status. Account updates revoke existing sessions.
- Mutating requests require a session CSRF token and reject a mismatched Origin header.
- Login/setup attempts are rate-limited in the database.
- Administrator and editor permissions are checked on the server. Folder scopes apply to writes, file management and source reads.
- Paths are confined to the mounted web root; hidden/parent paths and symbolic links are rejected.
- Save, replacement upload and restore take a per-path lock, compare the previous file hash, retain the previous bytes, and atomically replace the file.
- Image uploads are decoded/verified by Pillow. Server/executable file extensions are not accepted by the uploader. General uploads are limited to 100 MB; builder image uploads to 20 MB.
- Previewed site documents are sandboxed with scripts, forms, nested frames and network connections disabled. Public site scripts are retained in saved HTML; use the public site to test them.
- Account database, secrets, audit records and revision backups are outside the public website directory.
- The container runs without root, Linux capabilities or Docker socket access. Only the requested website mount and the private data volume are writable.

## Operational limits

This is not an independent security audit. Editors are trusted website authors; source editing can publish executable browser code on the public website. Protect editor accounts accordingly. Some legacy pages may be normalised by the browser when visually saved; keep and review the resulting backup. HTTPS proxy configuration must be completed before production logins.

Private backup history covers changes made through the editor, not edits made through SSH, Finder or other tools. Keep NAS backups. The app does not provide email recovery, automatic dependency updates or two-factor authentication. Restrict its network exposure as appropriate and keep the NAS/runtime patched.

Do not commit `.env` files, SSH keys, setup codes, cookie-signing keys, SQLite databases, private backups or production account credentials. The repository's test passwords are disposable test fixtures only.
