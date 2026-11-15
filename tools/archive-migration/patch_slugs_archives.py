from pathlib import Path
from urllib.parse import urlsplit,unquote,quote
import re,posixpath,html,json,collections
BASE=Path(__file__).parent/'slugs-source';OUT=Path(__file__).parent/'slugs-new'
files={x.split('\t')[0]for x in (BASE/'inventory.tsv').read_text().splitlines()}
fold=collections.defaultdict(list)
for x in files:fold[x.casefold()].append(x)
core={'index.html','photos.html','events.html','newsletters.html','writing.html','people.html','history.html','search.html','oddsand.html','about.html','Newsletters/index.html','Events/index.html','Photos/index.html'}
stats=collections.Counter();missing=collections.Counter();fixed=[]
def target(path):
 path=posixpath.normpath(path).lstrip('/')
 if path in ['.','']:path='index.html'
 if path.lower().startswith('old_luss_pages/slugs/'):path=path[len('old_luss_pages/Slugs/'):]
 if path.lower().endswith('.htm') and path[:-4]+'.html' in files:path=path[:-4]+'.html'
 elif path.lower().endswith('.html') and path[:-5]+'.htm' in files:path=path[:-5]+'.htm'
 for candidate in [path,path+'/index.html',path+'/index.htm',path+'/default.htm',path+'/INDEX.HTML',path+'/INDEX.HTM']:
  if candidate in files:return candidate
  if len(fold[candidate.casefold()])==1:return fold[candidate.casefold()][0]
 return None
def rewrite(url,current):
 value=html.unescape(url.strip())
 if not value or value.startswith(('#','javascript:','mailto:','data:','tel:')):return url
 try:u=urlsplit(value)
 except ValueError:return url
 if u.netloc and u.hostname not in ['slugs.xyz','www.slugs.xyz','slugs.granvillehouse.synology.me']:return url
 if u.scheme and u.scheme not in ['http','https']:return url
 path=unquote(u.path)
 if path.startswith('/new/'):path=path[5:]
 elif path.lower().startswith('/luss/slugs/'):path=path[len('/luss/Slugs/'):]
 elif path.lower().startswith('/luss/'):path='old_luss_pages/'+path[len('/luss/'):]
 elif path.startswith('/') or u.netloc:path=path.lstrip('/')
 else:path=posixpath.join(posixpath.dirname(current),path)
 hit=target(path)
 if not hit and not u.netloc:
  fallback=unquote(u.path).lstrip('./')
  if fallback.split('/')[0] in {'images','Events','Photos','Newsletters','Songs','Tresviso 2000','Tresviso 2005 web','Tresviso 2005 Pete','old_luss_pages','index.html','about.html','events.html','photos.html','oddsand.html','writing.html','slugs.css'}:hit=target(fallback)
 if not hit:
  if not u.netloc and not u.query and not value.startswith('?'):missing[(current,value)]+=1
  return url
 relative=posixpath.relpath(hit,posixpath.dirname(current)or '.')
 result=quote(relative,safe="/._-'()")+('?' +u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
 if result!=value:stats['links_normalised']+=1
 return result
attr=re.compile(r'(\b(?:href|src|background|action)\s*=\s*)([\"\'])(.*?)\2',re.I|re.S)
for p in (BASE/'html').rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(BASE/'html').as_posix()
 if rel in core:continue
 raw=p.read_bytes()
 try:text=raw.decode('utf-8');encoding='utf-8'
 except UnicodeDecodeError:text=raw.decode('cp1252',errors='replace');encoding='cp1252'
 text=attr.sub(lambda m:m[1]+m[2]+html.escape(rewrite(m[3],rel),quote=True)+m[2],text)
 # Correct legacy absolute refresh targets only if their destination is present.
 text=re.sub(r'(<meta\b[^>]*\bcontent\s*=\s*[\"\']\s*\d+\s*;\s*url\s*=\s*)([^\"\'>]+)',lambda m:m[1]+rewrite(m[2],rel),text,flags=re.I)
 if not re.search(r'<frameset\b',text,re.I):
  prefix=posixpath.relpath('.',posixpath.dirname(rel)or '.')
  def link(file):return quote(prefix+'/'+file,safe='/._-')
  bar=f'''<div id="slugs-archive-navigation" style="position:relative;z-index:9999;box-sizing:border-box;display:flex;flex-wrap:wrap;justify-content:center;gap:12px 22px;padding:12px 16px;background:#f6f4ed;border-bottom:1px solid #cbd2c4;font:12px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#203a32;text-align:center"><a style="color:#203a32;text-decoration:none;font-weight:700" href="{link('index.html')}">SLUGS archive</a><a style="color:#203a32" href="{link('photos.html')}">Photos</a><a style="color:#203a32" href="{link('events.html')}">Events</a><a style="color:#203a32" href="{link('newsletters.html')}">Newsletters</a><a style="color:#203a32" href="{link('search.html')}">Search</a></div>'''
  text,n=re.subn(r'(<body\b[^>]*>)',lambda m:m[1]+bar,text,count=1,flags=re.I)
  if n:stats['archive_pages_with_navigation']+=1
 dest=OUT/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_bytes(text.encode(encoding,errors='xmlcharrefreplace'))
 stats['archive_pages_processed']+=1
report={'changes':dict(stats),'unresolved_legacy_link_count':sum(missing.values()),'unresolved_legacy_links':[{'page':k[0],'target':k[1]}for k in missing]}
(BASE/'legacy-link-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'changes':dict(stats),'unresolved_legacy_links':sum(missing.values())},indent=2))
