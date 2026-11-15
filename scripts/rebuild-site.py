#!/usr/bin/env python3
"""Recreate the deployable static document root without contacting or changing the NAS."""
import argparse,shutil,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'dist/webroot');p.add_argument('--code-only',action='store_true',help='Stage only tracked files; preserve existing NAS photographs when deploying');args=p.parse_args();out=args.output.resolve()
if out==ROOT or out in (ROOT/'website/original',ROOT/'website/new') or ROOT.is_relative_to(out):p.error('Choose a separate output directory')
if out.exists() and any(out.iterdir()):p.error('Output directory must be empty; choose a new output path')
if not args.code_only:
 media=json.loads((ROOT/'reports/nas-media-manifest.json').read_text())
 missing=sum(not (ROOT/'website'/kind/x['path']).is_file() for kind,rows in media.items() for x in rows)
 if missing:p.error('Restore NAS photographs first with scripts/restore-media.py, or pass --code-only for a partial staging build')
out.mkdir(parents=True,exist_ok=True)
media=json.loads((ROOT/'reports/nas-media-manifest.json').read_text())
for kind,target in [('original',out),('new',out/'new')]:
 src=ROOT/'website'/kind;omitted={x['path'] for x in media[kind]}
 def ignore(directory,names):
  return [name for name in names if args.code_only and (Path(directory)/name).relative_to(src).as_posix() in omitted]
 shutil.copytree(src,target,dirs_exist_ok=True,ignore=ignore)
print('Rebuilt document root:',out)
if args.code_only:print('Code/assets staging only: do not delete existing NAS media when deploying.')
