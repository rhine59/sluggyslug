# Third-party materials

The editor bundles VvvebJs from the revision in `editor/VENDOR-REVISION.txt`. Its Apache-2.0 licence is in `editor/vendor/LICENSE`; upstream credits are retained in `editor/vendor/Credits.md`. Bundled libraries, fonts and icons retain their own notices in the vendored files.

Python runtime packages are specified in `editor/requirements.txt` and obtained from PyPI during the Docker build. Their licences apply independently.

The website archive's photographs, documents, music, text and gallery software retain their existing copyright and attribution notices. Inclusion in this private repository does not grant a new blanket licence to those materials.

HTML source formatting uses js-beautify v1.15.4 from https://github.com/beautifier/js-beautify, vendored as `editor/static/beautify-html.js`. Its MIT licence is in `editor/static/beautify-LICENSE`. Formatting runs locally in the browser.
