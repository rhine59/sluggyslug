#!/usr/bin/env python3
"""Inventory and hash the two checked-in website snapshots."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];out={}
for kind in ['original','new']:
 rows=[]
 for p in sorted((ROOT/'website'/kind).rglob('*')):
  if p.is_file():rows.append(dict(path=p.relative_to(ROOT/'website'/kind).as_posix(),size=p.stat().st_size,sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()))
 out[kind]=rows
(ROOT/'reports/website-manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print('Manifest:',{k:len(v) for k,v in out.items()})
