from pathlib import Path
from bs4 import BeautifulSoup
import urllib.request,urllib.parse,concurrent.futures,json,time,re,hashlib,html,collections
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--work-dir',type=Path,required=True);options=parser.parse_args();B=options.work_dir.resolve();OUT=B/'staged';D=OUT/'blog-reports';D.mkdir(parents=True,exist_ok=True)
feed=json.loads((B/'feed.json').read_text())['feed'];entries=feed['entry'];assert len(entries)==int(feed['openSearch$totalResults']['$t'])
landing=BeautifulSoup((B/'blog.html').read_text(),'html.parser');archive=landing.find(id='BlogArchive1');months={a['href']:a.get_text(' ',strip=True) for a in archive.select('a[href]') if re.search(r'/\d{4}/\d{2}/$',a['href'])}
def get(url):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SLUGS-archive-import/1.0'}),timeout=40) as r:return r.read(),r.headers.get_content_type()
  except Exception:
   if attempt==2:raise
   time.sleep(attempt+1)
def parallel(urls):
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:return dict(zip(urls,pool.map(get,urls)))
pages=parallel(list(months));archive_posts=set();monthposts={}
for url,(raw,_) in pages.items():
 soup=BeautifulSoup(raw,'html.parser');links={a['href'].split('?')[0] for a in soup.select('.post-title a[href], a[rel="bookmark"][href]') if re.match(r'https://slugsreports.blogspot.com/\d{4}/\d{2}/.+\.html',a['href'])};archive_posts|=links;monthposts[url]=sorted(links)
 expected=int(re.search(r'\((\d+)\)',str(archive.find('a',href=url).parent)).group(1));assert len(links)==expected,(url,len(links),expected)
urls=[next(x['href'] for x in e['link'] if x['rel']=='alternate') for e in entries];assert archive_posts==set(urls),(archive_posts-set(urls),set(urls)-archive_posts)
print('Verified all',len(months),'Blog Archive months and',len(urls),'post permalinks',flush=True)
posts=parallel(urls);old=json.loads((B/'event-metadata.json').read_text());meta={x['href']:x for x in old};mapping={url:urllib.parse.urlsplit(url).path.strip('/').replace('/','-') for url in urls};soups={};media=set();source_text={}
for url,(raw,_) in posts.items():
 soup=BeautifulSoup(raw,'html.parser');body=soup.select_one('.post-body');assert body is not None,url
 source_text[url]=body.get_text(' ',strip=True)
 for bad in body.select('script,iframe,object,embed,form,input,button'):bad.decompose()
 for tag in body.find_all(True):
  for attr in list(tag.attrs):
   if attr.lower().startswith('on') or attr in ['id','srcset','sizes','class','face','size','width','height']:del tag[attr]
  if tag.get('style'):
   align=re.search(r'(?:^|;)\s*text-align\s*:\s*(left|center|right)',tag['style']);tag.attrs.pop('style',None)
   if align:tag['style']='text-align:'+align[1]
  for attr in ['href','src']:
   if not tag.get(attr):continue
   absolute=urllib.parse.urljoin(url,tag[attr]);scheme=urllib.parse.urlsplit(absolute).scheme
   if scheme not in ['http','https','mailto','tel'] and not absolute.startswith('#'):del tag[attr];continue
   tag[attr]=absolute
   host=urllib.parse.urlsplit(absolute).hostname or ''
   if (attr=='src' and tag.name=='img') or (tag.name=='a' and (host.endswith('googleusercontent.com') or host.endswith('bp.blogspot.com'))):media.add(absolute)
  if tag.name=='img':tag['loading']='lazy';tag['alt']=tag.get('alt') or 'Photograph from '+meta[url]['title']
 assert body.get_text(' ',strip=True)==source_text[url],'Content changed during sanitisation: '+url
 soups[url]=body
print('Downloading',len(media),'image resources',flush=True)
media_map={};media_records=[];failures=[]
def download(url):
 try:
  raw,kind=get(url);assert kind.startswith('image/'),kind
  ext={'image/jpeg':'.jpg','image/png':'.png','image/gif':'.gif','image/webp':'.webp','image/avif':'.avif'}.get(kind,Path(urllib.parse.urlsplit(url).path).suffix.lower())
  assert ext in ['.jpg','.jpeg','.png','.gif','.webp','.avif'],ext
  name='media/'+hashlib.sha256(url.encode()).hexdigest()[:20]+ext;p=D/name;p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
  return url,name,{'path':'blog-reports/'+name,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'source':url}
 except Exception as e:return url,None,{'url':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for url,name,record in pool.map(download,sorted(media)):
  if name:media_map[url]=name;media_records.append(record)
  else:failures.append(record)
print('Saved',len(media_records),'images;',len(failures),'failures',flush=True)
if failures:raise RuntimeError(failures)
base=(B/'events-before.html').read_text();prefix=base.split('<main',1)[0];footer='<footer'+base.split('<footer',1)[1];footer=footer.split('<script type="application/json"',1)[0]+'</body></html>'
# Templates are copied from the live site so navigation stays consistent.
def frame(title,content):
 soup=BeautifulSoup(prefix+'<main id="main">'+content+'</main>'+footer,'html.parser')
 soup.title.string=title+' · SLUGS';soup.find('meta',attrs={'name':'description'})['content']=title+' — SLUGS Reports archive'
 for tag in soup.find_all(True):
  for attr in ['href','src']:
   v=tag.get(attr)
   if v and not re.match(r'(?:[a-z]+:|/|#)',v) and not tag.find_parent('main'):tag[attr]='../'+v
  if tag.has_attr('aria-current'):del tag['aria-current']
 style=soup.new_tag('style');style.string='.blog-content{max-width:850px;margin:2rem auto;overflow-wrap:anywhere}.blog-content img{max-width:100%;height:auto}.blog-content table{max-width:100%}.blog-content td{vertical-align:top}.blog-content p,.blog-content div{line-height:1.7}.report-nav{display:flex;gap:1rem;flex-wrap:wrap;margin:2rem 0}.blog-content h2,.blog-content h3{margin-top:1.5rem}';soup.head.append(style)
 return str(soup)
esc=lambda x:html.escape(x,quote=True)
records=[]
for url,body in soups.items():
 m=meta[url]
 for tag in body.find_all(True):
  for attr in ['href','src']:
   v=tag.get(attr)
   if v in mapping:tag[attr]=mapping[v]
   elif v in media_map:tag[attr]=media_map[v]
   elif v in months:tag[attr]='archive-'+urllib.parse.urlsplit(v).path.strip('/').replace('/','-')+'.html'
  if tag.name=='a' and tag.get('href','').startswith('http'):tag['rel']='noopener'
 content='<section class="page-intro shell"><p class="eyebrow">SLUGS REPORTS</p><h1>'+esc(m['title'])+'</h1><p>'+esc(m['date_label'])+' · Published '+next(e['published']['$t'][:10] for e in entries if url in [x.get('href') for x in e['link']])+'</p><p><a href="../events.html">← Events</a> · <a href="index.html">Blog Archive</a> · <a href="'+esc(url)+'">Original blog post ↗</a></p></section><article class="blog-content shell">'+''.join(str(x) for x in body.contents)+'</article>'
 name=mapping[url];(D/name).write_text(frame(m['title'],content));records.append({**m,'local':'blog-reports/'+name,'published':next(e['published']['$t'][:10] for e in entries if url in [x.get('href') for x in e['link']]),'text_sha256':hashlib.sha256(source_text[url].encode()).hexdigest()})
def listing(rows):return '<div class="entries">'+''.join('<article class="entry"><div><span class="eyebrow">'+esc(x['date_label'])+'</span><h3><a href="'+esc(Path(x['local']).name)+'">'+esc(x['title'])+'</a></h3></div><span class="entry-arrow">Read report →</span></article>' for x in sorted(rows,key=lambda x:x['date'],reverse=True))+'</div>'
monthlinks=[]
for url,label in sorted(months.items(),reverse=True):
 name='archive-'+urllib.parse.urlsplit(url).path.strip('/').replace('/','-')+'.html';rows=[x for x in records if x['href'] in monthposts[url]]
 (D/name).write_text(frame(label+' · Blog Archive','<section class="page-intro shell"><p class="eyebrow">BLOG ARCHIVE</p><h1>'+esc(label)+'</h1><p>Posts published this month. Event dates are shown below.</p><p><a href="index.html">← All reports and archive months</a> · <a href="'+esc(url)+'">Original archive month ↗</a></p></section><section class="shell">'+listing(rows)+'</section>'))
 monthlinks.append('<li><a href="'+name+'">'+esc(label)+'</a> ('+str(len(rows))+')</li>')
(D/'index.html').write_text(frame('SLUGS Reports · Blog Archive','<section class="page-intro shell"><p class="eyebrow">SLUGS REPORTS</p><h1>Blog Archive</h1><p>All '+str(len(records))+' reports and photographs from every month listed in the original blog’s Blog Archive. Reports below are in event-date order; month links use the blog publication dates.</p><p><a href="../events.html">← Events</a> · <a href="https://slugsreports.blogspot.com/">Original blog ↗</a></p></section><section class="shell"><h2>Blog Archive by publication month</h2><ul>'+''.join(monthlinks)+'</ul><h2>All reports — newest events first</h2>'+listing(records)+'</section>'))
# Change only the exact blog post destinations and a short explanatory line.
events=base
for url,name in mapping.items():
 needle='href="'+url+'"';assert events.count(needle)==1,(url,events.count(needle));events=events.replace(needle,'href="blog-reports/'+name+'"')
events=events.replace('Includes reports from the SLUGS Reports blog.','Includes complete reports and photographs from the SLUGS Reports blog. <a href="blog-reports/index.html">Browse every Blog Archive month</a>.',1)
assert events.count('<article')==base.count('<article')
(OUT/'events.html').write_text(events)
report={'source':'https://slugsreports.blogspot.com/','import_date':'2026-11-20','archive_months':[{'source':url,'label':months[url],'posts':monthposts[url]} for url in sorted(months,reverse=True)],'posts':records,'media':media_records,'media_failures':failures,'original_files_changed':False}
(B/'import-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('Prepared',len(records),'full reports,',len(months),'monthly archive pages, index and updated Events.',flush=True)
