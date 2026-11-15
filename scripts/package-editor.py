#!/usr/bin/env python3
"""Package only the checked-in application, never live accounts or private backups."""
import argparse,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'dist/slugs-editor-container.zip');args=p.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
excluded={'__pycache__','data','backups','locks','.git'}
with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted((ROOT/'editor').rglob('*')):
  rel=path.relative_to(ROOT/'editor')
  if not path.is_file() or any(v in excluded for v in rel.parts) or path.suffix in {'.pyc','.sqlite','.db','.pem','.key'} or path.name in {'setup-token','session-key','.env'}:continue
  z.write(path,rel.as_posix())
print('Created',args.output)
