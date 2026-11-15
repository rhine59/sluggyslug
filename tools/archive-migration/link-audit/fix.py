from pathlib import Path,PurePosixPath
from html.parser import HTMLParser
from urllib.parse import urlsplit,quote,unquote
import collections,json,posixpath,re,html
B=Path(__file__).parent;S=B/'source';O=B/'fixed';O.mkdir(exist_ok=True)
r=json.loads((B/'audit.json').read_text());files={x.split('\t')[0] for x in (B/'inventory.tsv').read_text().splitlines()};fold=collections.defaultdict(list);names=collections.defaultdict(list)
for f in files:fold[f.casefold()].append(f);names[PurePosixPath(f).name.casefold()].append(f)
changes=[];mapping={}
def resolve(x):
 p=x['target'];v=x['url'];u=urlsplit(v)
 if p=='..':return v,'valid original-site link'
 if x['problem']=='missing anchor':return v.split('#')[0] or PurePosixPath(x['page']).name,'removed nonexistent section anchor'
 if '@' in v and '/' not in v:return 'mailto:'+v,'repaired email link'
 if v.endswith('"'):
  t=posixpath.normpath(posixpath.join(posixpath.dirname(x['page']),unquote(v[:-1])))
  if t in files:return quote(posixpath.relpath(t,posixpath.dirname(x['page'])),safe='/'),'repaired stray quote'
 if p.lower().startswith('luss/slugs/'):
  t=p[len('luss/Slugs/'):]
  if t in files:return '/new/'+quote(t,safe='/'),'repaired former site path'
 candidates=[f for f in fold[p.casefold()] if '/.xvpics/' not in f]
 if not candidates:
  n=PurePosixPath(p).name.casefold();candidates=[f for f in names[n] if '/.xvpics/' not in f]
  # Prefer the exact missing directory suffix; never substitute an unrelated same-name photo.
  if n in ['background.gif','stonewhi.gif']:pass
  elif 'old_luss_pages/' in p:
   suffix='/'.join(p.split('/')[-2:]);exact=[f for f in candidates if f.endswith(suffix)]
   if exact:candidates=exact
   elif p.startswith('old_luss_pages/Pictures/'):
    full=[f for f in candidates if '/Images/' in f]
    if full:candidates=full
    if '/Other/Images/' in p:candidates=[f for f in candidates if '/HaggGill/Images/' in f]
   elif len(candidates)>1:candidates=[]
  elif 'Tony_Coghlan_web/' in p:candidates=[f for f in candidates if f.startswith(p.rsplit('/slides/',1)[0]+'/') and '/thumbs/' not in f]
  else:candidates=[]
 if len(candidates)==1:
  return quote(posixpath.relpath(candidates[0],posixpath.dirname(x['page']) or '.'),safe='/._-'),'recovered existing archive file'
 return None,'missing original content'
for x in r['bad']:
 new,reason=resolve(x)
 if reason=='valid original-site link':continue
 mapping[(x['page'],x['attr'],x['url'])]=(new,reason)
# Recreate the missing gallery slide, using its actual existing photo.
slide='images/Tony_Coghlan_web/1975 UK Yorkshire Dales/slides/1975 UK Yorkshire Dales 021.html'
photo=slide[:-5]+'.jpg'
if photo in files:
 q=O/slide;q.parent.mkdir(parents=True,exist_ok=True)
 q.write_text('<!doctype html><html><head><meta charset="utf-8"><title>1975 UK Yorkshire Dales 021</title></head><body><p><a href="../index.html">Back to album</a> | <a href="1975%20UK%20Yorkshire%20Dales%20020.html">Previous</a> | <a href="1975%20UK%20Yorkshire%20Dales%20022.html">Next</a></p><img style="max-width:100%;height:auto" src="1975%20UK%20Yorkshire%20Dales%20021.jpg" alt="1975 UK Yorkshire Dales 021"></body></html>')
 for x in r['bad']:
  if x['target']==slide:mapping.pop((x['page'],x['attr'],x['url']),None)
 changes.append(dict(page=slide,reason='recreated missing slide from existing photograph'))
class Fix(HTMLParser):
 def handle_starttag(self,tag,attrs):
  raw=self.get_starttag_text();new=raw;d=dict(attrs)
  for k,v in attrs:
   if (self.page,k,v) not in mapping:continue
   replacement,reason=mapping[self.page,k,v]
   pattern=r'(?<![\w:-])'+re.escape(k)+r'\s*=\s*(?:"[^"]*"|\x27[^\x27]*\x27|[^\s>]+)'
   if replacement is not None:new=re.sub(pattern,k+'="'+html.escape(replacement,quote=True)+'"',new,count=1,flags=re.I)
   elif tag=='link':
    new='';changes.append(dict(page=self.page,url=v,replacement=None,reason='removed obsolete missing editor metadata'));break
   elif k=='background':new=re.sub(pattern,'',new,count=1,flags=re.I)
   elif tag=='img' and k=='src':
    changes.append(dict(page=self.page,url=v,replacement=None,reason='missing original image labelled unavailable'))
    label=d.get('alt') or 'Archive image';new='<span class="slugs-unavailable" title="Original image is missing">['+html.escape(label)+': image unavailable]</span>';break
   elif k=='href':
    new=re.sub(pattern,'aria-disabled="true" title="Original archive file is missing"',new,count=1,flags=re.I)
    if tag=='a':new+='<small> [file unavailable]</small>'
   else:continue
   changes.append(dict(page=self.page,url=v,replacement=replacement,reason=reason))
  if new!=raw:
   line,col=self.getpos();start=self.offsets[line-1]+col;self.edits.append((start,start+len(raw),new))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
for p in S.rglob('*'):
 if p.suffix.lower() not in ['.htm','.html']:continue
 raw=p.read_bytes();enc='utf-8'
 try:s=raw.decode(enc)
 except UnicodeDecodeError:enc='cp1252';s=raw.decode(enc,errors='replace')
 q=Fix(convert_charrefs=True);q.page=p.relative_to(S).as_posix();q.edits=[];q.offsets=[0]
 for m in re.finditer('\n',s):q.offsets.append(m.end())
 q.feed(s)
 for a,b,v in reversed(q.edits):s=s[:a]+v+s[b:]
 if q.edits:
  o=O/q.page;o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(s.encode(enc,errors='xmlcharrefreplace'))
(B/'changes.json').write_text(json.dumps(changes,indent=2));print('Changed',len(list(O.rglob('*.html')))+len(list(O.rglob('*.htm'))),'pages;',len(changes),'repairs')
