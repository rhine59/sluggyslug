from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import posixpath,json,collections
B=Path(__file__).parent; S=B/'source'
files={x.split('\t')[0] for x in (B/'inventory.tsv').read_text().splitlines()}
refs=[];ids={}
class P(HTMLParser):
 def handle_starttag(self,t,a):
  d=dict(a)
  for k in ['id','name']:
   if d.get(k):self.ids.add(d[k])
  for k in ['href','src','background','action','poster','data']:
   if d.get(k):refs.append(dict(page=self.page,tag=t,attr=k,url=d[k]))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
for p in S.rglob('*'):
 if p.suffix.lower() not in ['.html','.htm']:continue
 q=P(convert_charrefs=True);q.page=p.relative_to(S).as_posix();q.ids=set()
 q.feed(p.read_bytes().decode('utf-8',errors='replace'));ids[q.page]=q.ids
bad=[];external=[];valid=[]
for r in refs:
 v=r['url'].strip()
 if not v or v.lower().startswith(('javascript:','mailto:','tel:','data:')):continue
 try:u=urlsplit(v)
 except ValueError:continue
 if u.netloc and u.hostname not in ['slugs.xyz','www.slugs.xyz','slugs.granvillehouse.synology.me']:
  external.append(r);continue
 if u.scheme and u.scheme not in ['http','https']:continue
 path=unquote(u.path)
 if path.startswith('/new/'):path=path[5:]
 elif path.startswith('/'):path=path.lstrip('/')
 elif not path:path=r['page']
 else:path=posixpath.join(posixpath.dirname(r['page']),path)
 path=posixpath.normpath(path)
 if path in ['.','']:path='index.html'
 if path not in files:
  for ix in ['index.html','index.htm','INDEX.HTML','INDEX.HTM']:
   if path+'/'+ix in files:path+='/'+ix;break
 r=dict(r,target=path,fragment=unquote(u.fragment))
 if path not in files:r['problem']='missing file';bad.append(r)
 elif u.fragment and path in ids and unquote(u.fragment) not in ids[path]:r['problem']='missing anchor';bad.append(r)
 else:valid.append(r)
report=dict(pages=len(ids),references=len(refs),bad=bad,external=external,valid=valid)
(B/'audit.json').write_text(json.dumps(report,indent=2))
print('pages',len(ids),'refs',len(refs),'bad',len(bad),'external',len(external))
for (u,why),n in collections.Counter((r['url'],r['problem']) for r in bad).most_common():print(n,why,u)
