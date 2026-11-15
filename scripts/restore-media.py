#!/usr/bin/env python3
"""Restore Git-excluded photographs from the existing NAS, then verify their hashes."""
from pathlib import Path
import argparse,json,shutil,hashlib,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();source=p.add_mutually_exclusive_group(required=True);source.add_argument('--local-root',type=Path,help='Mounted copy of /volume1/web/slugs');source.add_argument('--ssh',help='Authorised SSH host alias, for example slugs-nas');args=p.parse_args();manifest=json.loads((ROOT/'reports/nas-media-manifest.json').read_text())
for kind,rows in manifest.items():
 dest=ROOT/'website'/kind;dest.mkdir(parents=True,exist_ok=True)
 if args.ssh:
  with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8') as listing:
   listing.write(''.join(x['path']+'\n' for x in rows));listing.flush()
   remote='/volume1/web/slugs/'+('new/' if kind=='new' else '')
   subprocess.run(['rsync','-rlt','--partial','--checksum','--files-from='+listing.name,'-e','ssh -o BatchMode=yes',args.ssh+':'+remote,str(dest)+'/'],check=True)
 else:
  src=args.local_root/('new' if kind=='new' else '')
  for row in rows:
   target=dest/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
   if not target.exists():shutil.copy2(src/row['path'],target)
 for row in rows:
  f=dest/row['path']
  if not f.is_file() or hashlib.file_digest(f.open('rb'),'sha256').hexdigest()!=row['sha256']:raise SystemExit('Media differs from recorded snapshot: '+str(f))
 print('Verified',kind,len(rows),'NAS photograph files')
