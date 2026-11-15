# Test harness

## Automated editor tests

```sh
python3 -m venv .venv
.venv/bin/pip install -r editor/requirements.txt
.venv/bin/python -m unittest discover -s tests -p 'test_editor.py' -v
```

The harness creates a temporary miniature website and private data directory. It does not connect to the NAS or alter real website files. It checks authentication, disabled setup after initialisation, folder/role restrictions, traversal/symlink rejection, save conflicts, backup/restore, image/PDF uploads, invalid/executable upload rejection, overwrite protection, builder rendering, preview sandboxing, CSRF/Origin checks and session revocation. Seven test cases group these scenarios.

## Website checks

`python3 scripts/check-site.py` verifies available snapshot files against their manifests and checks HTML references in `/new`. Bulk photographs recorded in `nas-media-manifest.json` may be absent from a Git checkout; their references are checked against the recorded inventory. Restore them from the NAS to verify their bytes locally. The original snapshot is preserved as historical material and can still contain its original broken links. The dated link-repair report documents the earlier live audit; this offline check does not recontact every external site.

## Manual browser test already completed

A local Docker test container was run with a disposable copy of the homepage, Events page, CSS/images and a test HTML page. The visual builder loaded, text was edited by clicking the page, Save became enabled, and saving was confirmed on disk with a retained backup. This found and resolved two integration issues: direct typing did not immediately enable Save, and a font-list resource was initially omitted from the static routes.

## Deployment acceptance

NAS image build, HTTPS routing, production account setup and live disposable-page/upload tests remain outstanding until deployment. Follow DEPLOYMENT.md. A local successful test is not evidence that the NAS service is already live.

A GitHub Actions template is supplied in `ci/editor-tests.yml`; installing it under `.github/workflows/` requires a GitHub credential permitted to update workflows. The current Git credential does not have that scope, so the template is not enabled automatically. When enabled, it runs backend/repository tests and packaging/build checks. A full local website check requires the website assets; CI can use the committed manifests to avoid downloading the photo archive for every editor change.
