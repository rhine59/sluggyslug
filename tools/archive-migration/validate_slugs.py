from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import posixpath,json
root=Path(__file__).parent/'slugs-new'
known={x.split('\t')[0]for x in (root.parent/'slugs-source/inventory.tsv').read_text().splitlines()}
known|={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
class Audit(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ['href','src'] and value:
    u=urlsplit(value)
    if u.scheme or u.netloc or not u.path or u.path.startswith('../'):continue
    p=unquote(u.path)
    if p not in known:errors.append((page,p))
errors=[]
for page in ['index.html','photos.html','events.html','newsletters.html','writing.html','people.html','history.html','search.html']:
 Audit().feed((root/page).read_text())
print('New index link errors:',errors)
assert not errors
print('Verified all links and asset paths on the 8 new index pages.')
