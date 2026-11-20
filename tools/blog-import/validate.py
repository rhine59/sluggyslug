from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,unquote
import json,hashlib,posixpath
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--work-dir',type=Path,required=True);options=parser.parse_args();B=options.work_dir.resolve();stage=B/'staged';r=json.loads((B/'import-report.json').read_text());errors=[];checked=0
assert len(r['archive_months'])==19 and len(r['posts'])==28
assert {u for m in r['archive_months'] for u in m['posts']}=={p['href'] for p in r['posts']}
for post in r['posts']:
 soup=BeautifulSoup((stage/post['local']).read_text(),'html.parser');body=soup.select_one('.blog-content')
 assert hashlib.sha256(body.get_text(' ',strip=True).encode()).hexdigest()==post['text_sha256'],post['local']
 assert not body.select('script,iframe,object,embed,form'),post['local']
for p in stage.rglob('*.html'):
 soup=BeautifulSoup(p.read_text(),'html.parser')
 for tag in soup.select('[href],[src]'):
  for attribute in ['href','src']:
   value=tag.get(attribute)
   if not value:continue
   u=urlsplit(value)
   if u.scheme or u.netloc or not u.path:continue
   relative=posixpath.normpath(posixpath.join(p.relative_to(stage).parent.as_posix(),unquote(u.path)))
   target=stage/relative;fallback=Path(__file__).resolve().parents[2]/'website/new'/relative
   if not target.exists() and not fallback.exists():errors.append((str(p),value))
   checked+=1
assert not errors,errors[:20]
old=BeautifulSoup((B/'events-before.html').read_text(),'html.parser');new=BeautifulSoup((stage/'events.html').read_text(),'html.parser')
a=old.select('article.entry');b=new.select('article.entry');assert len(a)==len(b)==100
for before,after in zip(a,b):
 assert before.get_text(' ',strip=True)==after.get_text(' ',strip=True)
 oldhref=before.select_one('a').get('href','');newhref=after.select_one('a').get('href','')
 if 'slugsreports.blogspot.com' not in oldhref:assert oldhref==newhref
 else:assert newhref.startswith('blog-reports/')
print('PASS: all archive months/posts covered, all 28 report texts preserved, 100 Events entries unchanged,',checked,'local references resolve; no imported executable embeds.')
