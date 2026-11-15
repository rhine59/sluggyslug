from pathlib import Path
from html.parser import HTMLParser
import json,re,html
B=Path(__file__).parent;S=B/'source';O=B/'fixed';net=json.loads((B/'network.json').read_text());decisions={}
for x in net:
 u=x['url'];status=x['status']
 if status in [404,410] or (status==0 and 'nodename nor servname' in x.get('error','')):decisions[u]=(None,'external destination no longer available')
 elif status==200 and u.startswith('http://') and x.get('final')=='https://'+u[7:]:decisions[u]=(x['final'],'verified HTTPS replacement')
changes=json.loads((B/'external-changes.json').read_text()) if (B/'external-changes.json').exists() else []
class P(HTMLParser):
 def handle_starttag(self,t,a):
  raw=self.get_starttag_text();new=raw;d=dict(a)
  for k,v in a:
   if k not in ['href','src','background'] or v not in decisions:continue
   val,reason=decisions[v];pat=r'(?<![\w:-])'+re.escape(k)+r'\s*=\s*(?:"[^"]*"|\x27[^\x27]*\x27|[^\s>]+)'
   if val:new=re.sub(pat,k+'="'+html.escape(val,quote=True)+'"',new,count=1,flags=re.I)
   elif t in ['a','area'] and k=='href':
    new=re.sub(pat,'aria-disabled="true" data-original-href="'+html.escape(v,quote=True)+'"',new,count=1,flags=re.I)
    if t=='a':new+='<small> [external site unavailable]</small>'
   elif k=='background':new=re.sub(pat,'',new,count=1,flags=re.I)
   elif t=='img' and k=='src':new='<span title="Original external image is unavailable">['+html.escape(d.get('alt') or 'External image')+': unavailable]</span>'
   else:continue
   changes.append(dict(page=self.page,url=v,replacement=val,reason=reason))
  if raw!=new:
   l,c=self.getpos();start=self.offsets[l-1]+c;self.edits.append((start,start+len(raw),new))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
for p in S.rglob('*'):
 if p.suffix.lower() not in ['.html','.htm']:continue
 rel=p.relative_to(S);src=O/rel if (O/rel).exists() else p;raw=src.read_bytes();enc='utf-8'
 try:s=raw.decode(enc)
 except UnicodeDecodeError:enc='cp1252';s=raw.decode(enc,errors='replace')
 q=P(convert_charrefs=True);q.page=rel.as_posix();q.edits=[];q.offsets=[0]+[m.end() for m in re.finditer('\n',s)];q.feed(s)
 for a,b,v in reversed(q.edits):s=s[:a]+v+s[b:]
 if q.edits:
  dest=O/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(s.encode(enc,errors='xmlcharrefreplace'))
(B/'external-changes.json').write_text(json.dumps(changes,indent=2));print('External repairs',len(changes),'distinct URL decisions',len(decisions))
