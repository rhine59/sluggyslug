#!/usr/bin/env python3
"""Package shell source/docs/tests only; never access lists or private host keys."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'dist/slugs-shell-container.zip';out.parent.mkdir(exist_ok=True)
names=['Dockerfile','sshd_config','entrypoint.sh','deploy.sh','rebuild.sh','test-running.sh','README.md','.dockerignore']
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for name in names:z.write(ROOT/'shell'/name,name)
 z.write(ROOT/'tests/test_shell_integration.py','tests/test_shell_integration.py')
print(out)
