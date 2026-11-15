#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname "$script_dir")
cd "$repo_dir"
python_bin=${PYTHON:-python3}
"$python_bin" -m unittest discover -s tests -p 'test_*.py' -v
"$python_bin" scripts/package-editor.py
if [ -f reports/website-manifest.json ] && [ -d website/new ]; then
  "$python_bin" scripts/check-site.py
fi
