#!/usr/bin/env python3
"""Check checked-in bytes and local HTML/CSS references; no network requests."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,urljoin,unquote
import argparse,json,hashlib,re
ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--links-only',action='store_true');args=p.parse_args();manifest=json.loads((ROOT/'reports/website-manifest.json').read_text());errors=[];refs=[];ids={}
omitted=json.loads((ROOT/'reports/nas-media-manifest.json').read_text())
nas_only={k:{x['path'] for x in v} for k,v in omitted.items()}
skipped=0
files={k:{x['path'] for x in v} for k,v in manifest.items()}
if not args.links_only:
 for kind,rows in manifest.items():
  for row in rows:
   f=ROOT/'website'/kind/row['path']
   if not f.is_file():
    if row['path'] in nas_only.get(kind,set()):skipped+=1;continue
    errors.append('Missing snapshot file: '+kind+'/'+row['path']);continue
   if f.stat().st_size!=row['size'] or hashlib.file_digest(f.open('rb'),'sha256').hexdigest()!=row['sha256']:errors.append('Changed snapshot bytes: '+kind+'/'+row['path'])
class Parser(HTMLParser):
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  for k in ['href','src','background','poster','data','action']:
   if d.get(k):refs.append((self.page,d[k]))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
for f in (ROOT/'website/new').rglob('*'):
 if not f.is_file():continue
 if f.suffix.lower() in ['.html','.htm']:
  q=Parser();q.page=f.relative_to(ROOT/'website/new').as_posix();q.feed(f.read_bytes().decode('utf-8',errors='replace'))
 if f.suffix.lower()=='.css':
  for u in re.findall(r'url\(\s*[\"\x27]?([^\)\"\x27]+)',f.read_text(errors='replace'),re.I):refs.append((f.relative_to(ROOT/'website/new').as_posix(),u))
checked=0
for page,value in refs:
 if not value.strip() or value.startswith(('#','data:','javascript:','mailto:','tel:')):continue
 try:u=urlsplit(urljoin('https://slugs.granvillehouse.synology.me/new/'+page,value))
 except ValueError:continue
 if u.hostname!='slugs.granvillehouse.synology.me':continue
 path=unquote(u.path);kind='new' if path=='/new' or path.startswith('/new/') else 'original';rel=path[5:] if path.startswith('/new/') else '' if path=='/new' else path.lstrip('/')
 candidates=[rel]+[rel.rstrip('/')+'/'+x for x in ['index.html','index.htm','INDEX.HTML','INDEX.HTM']]
 if not rel:candidates=['index.html','index.htm']
 if not any(x in files[kind] for x in candidates):errors.append(page+' -> '+value)
 checked+=1
print('Checked',checked,'local references; NAS-only photographs not downloaded:',skipped)
if errors:
 print('\n'.join(errors[:60]));print(len(errors),'failures');raise SystemExit(1)
print('Snapshot integrity and local-reference checks passed')
