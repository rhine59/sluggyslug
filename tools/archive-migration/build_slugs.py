from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit,quote
import json,re,html,posixpath,collections,shutil
BASE=Path(__file__).parent/'slugs-source'; OUT=Path(__file__).parent/'slugs-new';OUT.mkdir(exist_ok=True)
ASSETS=OUT/'assets';ASSETS.mkdir(exist_ok=True)
files={x.split('\t')[0]:int(x.split('\t')[1]) for x in (BASE/'inventory.tsv').read_text().splitlines()}
fold=collections.defaultdict(list)
for f in files:fold[f.casefold()].append(f)
FIXES=[]; MISSING=[]
def esc(x):return html.escape(str(x),quote=True)
def clean(x):return re.sub(r'\s+',' ',x.replace('\ufffd',"'")).strip()
def resolve(href):
 u=urlsplit(href)
 if u.scheme or u.netloc:return href
 path=posixpath.normpath(unquote(u.path)).lstrip('./')
 candidates=[path,path+'/index.html',path+'/index.htm',path+'/default.htm',path+'/INDEX.HTML',path+'/INDEX.HTM']
 hit=next((x for x in candidates if x in files),None)
 if not hit:
  for x in candidates:
   if len(fold[x.casefold()])==1:hit=fold[x.casefold()][0];break
 if not hit:return None
 if path!=hit and not hit.startswith(path+'/'):FIXES.append({'from':href,'to':hit})
 return quote(hit,safe="/._-'()")+('?#'[0]+u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
class Links(HTMLParser):
 def __init__(self):super().__init__();self.a=None;self.section='';self.heading=None;self.out=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=='p' and d.get('class')=='page_title':self.heading=[]
  if t=='a' and 'href'in d:self.a={'href':d['href'],'text':[],'section':self.section}
 def handle_data(self,s):
  if self.a is not None:self.a['text'].append(s)
  if self.heading is not None:self.heading.append(s)
 def handle_endtag(self,t):
  if t=='p' and self.heading is not None:self.section=clean(''.join(self.heading));self.heading=None
  if t=='a' and self.a is not None:
   self.a['text']=clean(''.join(self.a['text']));self.out.append(self.a);self.a=None
for source_name in ['events.html','photos.html','oddsand.html','writing.html']:
 source_page=BASE/'html'/source_name
 if source_page.exists():
  parser=Links();parser.feed(source_page.read_bytes().decode('utf-8',errors='replace'))
  (BASE/(source_name+'.links.json')).write_text(json.dumps(parser.out,indent=2))
catalog=[]
def item(title,href,kind,year='',description='',image=None):
 url=resolve(href)
 record={'title':clean(title),'href':url,'kind':kind,'year':str(year),'description':description,'image':image}
 if not url:MISSING.append({'title':title,'path':href})
 else:catalog.append({k:v for k,v in record.items() if k!='image'})
 return record
NAV=[('index.html','Home'),('photos.html','Photos'),('events.html','Events'),('newsletters.html','Newsletters'),('writing.html','Writing'),('people.html','People'),('history.html','Club history')]
def header(active):
 nav=''.join(f'<a href="{u}"'+(' aria-current="page"'if u==active else '')+f'>{t}</a>'for u,t in NAV)
 return f'''<a class="skip" href="#main">Skip to content</a><div class="masthead"><div class="shell mast-inner"><span>Society of Lancaster University Graduate Speleologists</span><a href="../">Original site ↗</a></div></div><header class="site-header"><div class="shell header-inner"><a class="brand" href="index.html" aria-label="SLUGS home"><span class="brand-mark" aria-hidden="true">S</span><span>SLUGS<span class="brand-small">THE CLUB ARCHIVE</span></span></a><nav aria-label="Main navigation">{nav}</nav><a class="search-link" href="search.html" aria-label="Search the archive"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg></a></div></header>'''
def footer():return '''<footer class="site-footer"><div class="shell footer-inner"><div><a class="footer-brand" href="index.html">SLUGS</a><p>Old enough to know better. Still sluggy.</p><p class="fine">Photographs © Slug Ink or their credited contributors.</p></div><div><a href="history.html">About & credits</a><a href="search.html">Search the archive</a><a href="../">Original site ↗</a></div><p class="fine">Friends, caves and shared adventures.<br>Since Clapdale, 1976.</p></div></footer>'''
def write(name,title,body,description='Explore the SLUGS archive of photographs, events, newsletters and club history.'):
 data=json.dumps(catalog,ensure_ascii=False).replace('<','\\u003c') if name=='search.html' else '[]'
 (OUT/name).write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(description)}"><meta name="robots" content="noindex,follow"><meta name="theme-color" content="#203c34"><title>{esc(title)} · SLUGS</title><link rel="stylesheet" href="assets/site.css"><script defer src="assets/site.js"></script></head><body>{header(name)}<main id="main">{body}</main>{footer()}<script type="application/json" id="archive-data">{data}</script></body></html>''')
def intro(kicker,title,description):return f'<section class="page-intro shell"><p class="eyebrow">{esc(kicker)}</p><h1>{title}</h1><p class="lede">{description}</p></section>'
def card(r):
 if not r['href']:return f'<article class="entry unavailable"><div><span class="eyebrow">{esc(r["kind"])}</span><h3>{esc(r["title"])}</h3><p>This page was linked from the original site, but its file is not in the copied archive.</p></div><span class="status">Page unavailable</span></article>'
 ext=urlsplit(r['href']).scheme
 tag='External link ↗' if ext else ('PDF document'if r['href'].lower().endswith('.pdf') else 'Open collection →'if r['kind']in ['Photo collection','Event report'] else 'Read →')
 image=f'<img src="{r["image"]}" alt="" loading="lazy">'if r.get('image') else ''
 return f'<article class="entry" data-search="{esc(" ".join([r["title"],r["year"],r["description"],r["kind"]]))}" data-year="{esc(r["year"])}">{image}<div><span class="eyebrow">{esc(r["year"] or r["kind"])}</span><h3><a href="{esc(r["href"])}">{esc(r["title"])}</a></h3>'+ (f'<p>{esc(r["description"])}</p>'if r['description'] else '')+f'</div><span class="entry-arrow" aria-hidden="true">{tag}</span></article>'
def section(title,records,id=None,subtitle=''):
 return f'<section class="archive-section shell"'+(f' id="{id}"'if id else '')+f'><div class="section-heading"><div><p class="eyebrow">{len(records)} '+('entries'if len(records)!=1 else 'entry')+f'</p><h2>{esc(title)}</h2></div>'+(f'<p>{esc(subtitle)}</p>'if subtitle else '')+'</div><div class="entries">'+''.join(map(card,records))+'</div></section>'
def filters(noun,years=None):
 options='<option value="">All years</option>'+''.join(f'<option>{x}</option>'for x in years or [])
 return '<div class="shell"><div class="filter-bar"><label class="filter-label">Find '+noun+'<input type="search" data-filter placeholder="Search titles, places or years…"></label>'+('<label>Year<select data-year-filter>'+options+'</select></label>'if years else '')+'<p class="filter-count" aria-live="polite" data-filter-count></p></div><p class="no-results" data-no-results hidden>No matches. Try another word or year.</p></div>'
# Events: preserve every original report link, then surface albums absent from the old index.
events=[];seen=set()
for a in json.loads((BASE/'events.html.links.json').read_text()):
 if not re.fullmatch(r'\d{4}',a['section']):continue
 if a['href'].startswith(('brain_of_a_slug','images/2002dinner/xtra')) or a['href'] in ({u for u,t in NAV}|{'oddsand.html'}):continue
 if a['text'] in ['Photos I','Photos II']:a['text']='Aviemore, March — '+a['text']
 a['text']=a['text'].replace('Octobery','October').replace('Sawmill_Cottage','Sawmill Cottage').replace('Ecton_Mines','Ecton Mines')
 r=item(a['text'],a['href'],'Event report',a['section'])
 if r['href'] and r['href'] not in seen:events.append(r);seen.add(r['href'])
for f in files:
 if re.match(r'Events/[^/]+/index\.(html?|HTML?)$',f):
  url=resolve(f)
  if url in seen:continue
  folder=f.split('/')[1];m=re.match(r'(\d\d)[_ -]',folder)
  year='20'+m[1] if m else ('2005' if folder=='Nicole18th' else '')
  title=re.sub(r'^\d\d[_ -](\d\d[_ -])?','',folder).replace('_',' ').strip()
  if folder=='Nicole18th':title='Nicole’s eighteenth birthday — photo album'
  r=item(title,f,'Event report',year,'An additional album from the club archive.')
  if r['href']:events.append(r);seen.add(r['href'])
# Photo records: explicit labels retain contributors and the original context.
photo_specs=[
('Lancaster & Clapdale','Early LUSS, 1968–69','images/JohnSellers/',1968,'John Sellers'),
('Lancaster & Clapdale','UK photographs, 1970','images/Tony_Coghlan_web/1970 UK Various/',1970,'Tony Coghlan'),
('Lancaster & Clapdale','UK photographs, 1971','images/Tony_Coghlan_web/1971 UK Various/',1971,'Tony Coghlan'),
('Lancaster & Clapdale','LUSS in the 1970s','images/Elaine/','1970s','Elaine'),
('Lancaster & Clapdale','Percy Road in the 1970s','images/PercyRoad/','1970s',''),
('Lancaster & Clapdale','Yorkshire Dales, 1974','images/Tony_Coghlan_web/1974 UK Yorkshire Dales/',1974,'Tony Coghlan'),
('Lancaster & Clapdale','Yorkshire Dales, 1975','images/Tony_Coghlan_web/1975 UK Yorkshire Dales/',1975,'Tony Coghlan'),
('Lancaster & Clapdale','Clapdale, 1978','images/1978_Doth/',1978,'Doth'),
('Lancaster & Clapdale','Ireland, January 1979','images/79_January_Ireland/',1979,'Doth'),
('Lancaster & Clapdale','SLUGS in the 1970s–80s','https://photos.app.goo.gl/BZ9dRHP83rZWiWku7','1970s–80s','Fran Bagenal · external album'),
('Lancaster & Clapdale','Clapdale barn','images/early_barn.jpg','','University publicity photograph'),
('Lancaster & Clapdale','Clapdale kitchen','images/kitchen_wallpaper.jpg','','University publicity photograph'),
('Spain & Tresviso','Spain expedition, 1970','images/Tony_Coghlan_web/1970 Spain Expedition/',1970,'Tony Coghlan'),
('Spain & Tresviso','Spain expedition, 1971','images/Tony_Coghlan_web/1971 Spain Expedition/',1971,'Tony Coghlan'),
('Spain & Tresviso','Ojo Guareña, 1971','images/Tony_Coghlan_web/1971 Spain Ojo Guarena/',1971,'Tony Coghlan'),
('Spain & Tresviso','Tresviso: a box in a loft','images/Luss_Tresviso_box_in_loft/','','Rediscovered photographs'),
('Spain & Tresviso','Agua, 1975–78','https://photos.app.goo.gl/aGYpsNiGhxCtBZPJA','1975–78','Fran Bagenal · external album'),
('Spain & Tresviso','Tresviso 1976 — Doth','images/tresviso76/Doth/',1976,'Including the return journey through France'),
('Spain & Tresviso','Tresviso 1976 — Phil & Rosie','images/tresviso76/PhilandRosie/',1976,'Phil and Rosie'),
('Spain & Tresviso','LUSS, 1976 — Paul Simm','images/tresviso76/PaulSimm1/',1976,'Paul Simm'),
('Spain & Tresviso','Tresviso village, 1976','images/tresviso76/PaulSimm2/',1976,'Paul Simm'),
('Spain & Tresviso','Tresviso, 1977','images/tresviso77_Paul Simm',1977,'Paul Simm'),
('Spain & Tresviso','Spanish caving permit, 1977','images/santander_permit_77.gif',1977,'An expedition document'),
('Spain & Tresviso','Tresviso 1980 — Doth','images/tresviso80/Doth/',1980,'Doth'),
('Spain & Tresviso','Tresviso 1980 — down the back of the settee','images/tresviso80/dtbots/',1980,'Rediscovered photographs'),
('Spain & Tresviso','Tresviso 2000 website','Tresviso 2000/index.htm',2000,'George Shaw and Sue Ianson'),
('Spain & Tresviso','Tresviso 2000 — Fran Bagenal','https://photos.app.goo.gl/APRUTctZvaNdT8Cb8',2000,'External album'),
('Spain & Tresviso','Tresviso 2000 — Paul Simm','Photos/Tresviso2000PaulSimm',2000,'Paul Simm'),
('Spain & Tresviso','Tresviso 2005 — Phil & Rosie','Tresviso 2005 web/Tresviso_2005.htm',2005,'Phil and Rosie'),
('Spain & Tresviso','Tresviso 2005 — Pete Owens','Tresviso 2005 Pete',2005,'Pete Owens'),
('Spain & Tresviso','Tresviso 2005 — Paul Simm','http://www.pes-systems.net/photos/tresviso2005/',2005,'External album'),
('Spain & Tresviso','Tresviso, 2025','images/tresviso2025/index.html',2025,'Photographs from various contributors'),
('People & collections',"John Boardman’s shoe box in the attic",'Photos/John_Boardmans_Shoe_Box_in_the_Attic/index.html','','A collection of trips, celebrations and memories'),
('People & collections','Carolyn Ginnever','images/CarolynG/index.htm','',''),
('People & collections','Annual dinner, 1975','images/annualdinner75.jpg',1975,'Chris Baxter'),
('People & collections','Kingsdale Master Cave in fancy dress','images/kmc78.jpg',1978,'Chris Baxter · before the annual dinner'),
('Films','Tresviso 1978: with our friends in the village','https://www.youtube.com/watch?v=-BZwIiDm7m8',1978,'Chris Baxter · YouTube'),
('Films','Tresviso 1979','https://www.youtube.com/watch?v=jdlVkVcamuQ',1979,'Remastered by Chris Baxter · YouTube'),
('Films','Descent into Death Crevasse','https://www.youtube.com/watch?v=axUmCz0wjZc','','Chris Baxter · YouTube')]
photos=collections.defaultdict(list)
for group,title,path,year,credit in photo_specs:photos[group].append(item(title,path,'Film'if group=='Films'else'Photo collection',year,credit))
# Newsletters: label the documents from their filenames; preserve original document files.
newsletter_names={
'November95.html':('November 1995','1995'),'May96.html':('May 1996','1996'),'October96.html':('October 1996','1996'),'September97.html':('September 1997','1997'),'April99.html':('April 1999','1999'),'April00.htm':('April 2000','2000'),'October00.htm':('October 2000','2000'),'December00.htm':('December 2000','2000'),'June01.htm':('June 2001','2001'),'Nov2001.htm':('November 2001','2001'),'Mar02.htm':('March 2002','2002'),'Oct02.htm':('October 2002','2002'),'Mar03.htm':('March 2003','2003'),'Apr04.htm':('April 2004','2004'),'events_AUG_to_xmas_05.htm':('Events: August–Christmas 2005','2005'),'events_SEPT_06_to_Easter_07.htm':('Events: September 2006–Easter 2007','2006'),'Mar07.htm':('March 2007','2007'),'07May.htm':('Events: May–December 2007','2007'),'08Jan.htm':('Events: January–July 2008','2008'),'events_Nov_08.htm':('Events: November 2008–April 2009','2008'),'Slugs_Events_October_09.htm':('Events: October 2009','2009'),'SLUGS_EVENTS_2011.htm':('Events: 2011','2011'),'SLUGS_EVENTS_AUTUM_ 2011.htm':('Autumn 2011','2011'),'SLUGS_EVENTS_AUTUM_ 2012.htm':('Autumn 2012','2012'),'SLUGS EVENTS JANUARY TO JULY 2013.htm':('Events: January–July 2013','2013'),'Slugs_Events_Autumn_2013.htm':('Autumn 2013','2013'),'SLUGS_EVENTS_2016.htm':('Events: 2016','2016')}
news=[item(title,'Newsletters/'+name,'Newsletter',year)for name,(title,year)in newsletter_names.items()]
if 'events2017.pdf' in files:news.append(item('SLUGS events, 2017','events2017.pdf','Newsletter','2017','The original events circular, as a PDF.'))
extras=[item('SLUGS dinner, 2002','Newsletters/dinner02.htm','Club document','2002'),item('SLUGS dinner, 2004','Newsletters/dinner04.htm','Club document','2004'),item('Party information','Newsletters/party-web.html','Club document'),item('Aquarius 2','Newsletters/Aquarius2.pdf','Club document'),item('Events: November 2008 — Word document','Newsletters/SLUGS EVENTS  November 08.doc','Club document','2008'),item('Events: 2016 — Word document','Newsletters/SLUGS_EVENTS_2016.docx','Club document','2016'),item('Newsletter archive page','Newsletters/rr.htm','Club document')]
writing=[item('The Caver','writing/the_caver.jpg','Writing','1982','Dave Checkley · a poem written on the expedition while exploring 56.'),item('Slugs at Symonds Yat','writing/symonds_yat.pdf','Writing','','Jes · a SLUGS weekend in the Wye Valley.'),item("A Slug’s a Slug for a’ that",'writing/a_slug.pdf','Writing','','From the original collection, attributed to Robbie Burns and discovered by Phil Chapman.')]
people=[item('Alex (Peter Alexander)','alex.htm','Remembrance','','In memoriam by Chris Baxter.'),item('Angus: Requiem at Loch Tull','angus.htm','Remembrance','','Jerry Peterson.'),item('Jonah (Howard Rothwell)','Jonah.htm','Remembrance','','In memoriam by Chris Baxter.'),item('Tony Harrison','http://myweb.tiscali.co.uk/ticketyboo1/tony.htm','Remembrance','','A family page · external historical link.'),item('Tony Hammes','Tony_h.htm','Remembrance','','Tony’s funeral, by Ken.'),item('Dave Checkley: obituary from Descent','dc_descent_obit.pdf','Remembrance','','Colin Boothroyd and Howard Jones.'),item('Dave Checkley & Chas Yonge: BCRA obituaries','dc_chas_bcra_obit.pdf','Remembrance')]
if 'Tony_funeral.pdf' in files:people.append(item('Tony’s funeral — PDF account','Tony_funeral.pdf','Remembrance','','An additional account from the original collection.'))
history=[item('The old LUSS pages','old_luss_pages/index.html','Club history','','The earlier society website, preserved as an archive.'),item('The LUSS song book','Songs/index.html','Club history','','Songs from the original collection.'),item('Brain of a Slug','brain_of_a_slug/default.htm','Club history','','The Up All Night Productions quiz.'),item('Clapdale vehicle pass','images/vehicleauth.gif','Club history'),item('LUSS T-shirt artwork','images/lusst.jpg','Club history'),item('Slug on a carbide lamp','images/slug-on-a-carbide_l.gif','Club history'),item('Slug on a carbide lamp — another version','images/slug-on-a-carbide-2.jpg','Club history','','From Sue I’Anson.')]
links=[item('Tresviso Caves Project','http://www.tresvisocaves.info/','External resource'),item('Tresviso Caves Project blog','http://www.tresvisocaves.info/blog/','External resource'),item('Lancaster University history','http://www.lancs.ac.uk/unihistory/index.htm','External resource','','Historical photographs and footage from the university archives.')]
# Optimised, real photographs from the copied site.
from PIL import Image
for source,name in [(3,'patterdale.jpg'),(2,'tresviso.jpg'),(4,'clapdale.jpg'),(5,'early-luss.jpg')]:
 im=Image.open(BASE/f'candidate-{source}.jpg').convert('RGB');im.thumbnail((1500,1200));im.save(ASSETS/name,quality=86,optimize=True)
# Home
counts={'photos':sum(map(len,photos.values())),'events':len(events),'news':len(news)}
body=f'''<section class="hero shell"><div class="hero-copy"><p class="eyebrow"><span class="small-rule"></span> FRIENDS ABOVE & BELOW GROUND</p><h1>Old enough to<br>know better.<br><em>Still sluggy.</em></h1><p class="hero-description">The photographs, stories and shared adventures of the Society of Lancaster University Graduate Speleologists.</p><div class="hero-actions"><a class="button" href="photos.html">Explore the photo archive <span>↗</span></a><a class="text-link" href="history.html">Our story →</a></div><div class="hero-footnote"><span class="sun-mark" aria-hidden="true">✳</span><span>Founded at Clapdale in 1976.<br>Still no rules. Still plenty of stories.</span></div></div><figure class="hero-image"><img src="assets/patterdale.jpg" alt="Snow-dusted fells reflected in Angle Tarn on a SLUGS Patterdale weekend" fetchpriority="high"><figcaption><span>ANGLE TARN, PATTERDALE</span><span>Club meet · 2017</span></figcaption><span class="photo-index" aria-hidden="true">01 / THE ARCHIVE</span></figure></section>
<section class="archive-strip"><div class="shell strip-inner"><span>A lifetime of getting out there.</span><a href="photos.html">{counts['photos']} photo & film collections ↗</a><a href="events.html">{counts['events']} event reports ↗</a><a href="newsletters.html">{counts['news']} newsletters ↗</a></div></section>
<section class="shell home-section"><div class="section-heading"><div><p class="eyebrow">FIND YOUR WAY AROUND</p><h2>Good times. Kept together.</h2></div><p>Start with a place, a year or a familiar face.</p></div><div class="feature-grid"><a class="feature feature-large" href="photos.html#spain"><img src="assets/tresviso.jpg" alt="The limestone landscape near Tresviso" loading="lazy"><div><p class="eyebrow">SPAIN & TRESVISO</p><h3>Back to the Picos.</h3><p>Expeditions, village life and return visits, from 1970 to 2025.</p><span>Explore the collections ↗</span></div></a><a class="feature" href="photos.html#lancaster"><img src="assets/clapdale.jpg" alt="An archival photograph at the stone doorway of Clapdale, 1978" loading="lazy"><div><p class="eyebrow">LANCASTER & CLAPDALE</p><h3>Where it all began.</h3><p>The early LUSS years, Percy Road and life at the barn.</p><span>Open the photo archive ↗</span></div></a><a class="feature feature-plain" href="events.html"><div><p class="eyebrow">THE EVENT ARCHIVE</p><h3>Remember<br>that weekend?</h3><p>Caves, hills, bikes, birthdays and the occasional banquet. Browse the reports by year.</p><span>Find a club meet ↗</span></div><span class="line-art" aria-hidden="true">1976<br>↘<br>TODAY</span></a></div></section>
<section class="shell home-section latest"><div><p class="eyebrow">A RECENT RETURN</p><h2>Tresviso, 2025.</h2><p>Another visit. More photographs. Revisit the village and the mountains in the newest photo collection in the archive.</p><a class="button button-light" href="images/tresviso2025/index.html">View the 2025 photographs ↗</a></div><div class="quick-links"><a href="newsletters.html"><span>01</span><div><h3>From the newsletter pile</h3><p>Club news and plans, 1995–2017.</p></div><b aria-hidden="true">↗</b></a><a href="writing.html"><span>02</span><div><h3>A few well-chosen words</h3><p>Poems and writing from the collection.</p></div><b aria-hidden="true">↗</b></a><a href="people.html"><span>03</span><div><h3>Remembering friends</h3><p>Tributes, memories and obituaries.</p></div><b aria-hidden="true">↗</b></a></div></section>
<section class="shell find-section"><div><p class="eyebrow">LOOKING FOR SOMETHING?</p><h2>A name. A place. A year.</h2></div><form action="search.html" class="search-form" role="search"><label class="sr-only" for="home-search">Search the archive</label><input id="home-search" name="q" type="search" placeholder="Try Tresviso, Borrowdale or 1976…"><button class="button" type="submit">Search →</button></form></section>'''
write('index.html','Home',body)
# Browse pages
body=intro('THE PHOTO ARCHIVE','Faces, places<br>& <em>far-flung adventures.</em>','Photographs and films from the early LUSS years to return visits in 2025. Original albums and contributor credits are kept together.')
body+='<div class="shell"><div class="jump-links" aria-label="Photo sections">'+''.join(f'<a href="#{id}">{label} ↓</a>'for label,id in [('Lancaster & Clapdale','lancaster'),('Spain & Tresviso','spain'),('People & collections','collections'),('Films','films')])+'</div></div>'+filters('a collection')
for group,id in [('Lancaster & Clapdale','lancaster'),('Spain & Tresviso','spain'),('People & collections','collections'),('Films','films')]:body+=section(group,photos[group],id)
write('photos.html','Photos',body)
years=sorted({r['year']for r in events if r['year']},reverse=True)
body=intro('THE EVENT ARCHIVE','Remember<br><em>that weekend?</em>','Caving, walking, cycling, parties and reunions. Browse the club reports by year, or search for a place or event.')+filters('an event',years)
for year in years:body+=section(year,[r for r in events if r['year']==year])
if any(not r['year']for r in events):body+=section('More from the archive',[r for r in events if not r['year']])
write('events.html','Events',body)
body=intro('LETTERS FROM THE CLUB','News, plans<br>& <em>the odd good idea.</em>','The newsletters and event circulars, brought into one index. These are historical documents; dates and arrangements refer to their original publication.')+filters('a newsletter',sorted({r['year']for r in news},reverse=True))
for year in sorted({r['year']for r in news},reverse=True):body+=section(year,[r for r in news if r['year']==year])
body+=section('More club documents',extras)
write('newsletters.html','Newsletters',body)
write('writing.html','Writing',intro('FROM THE COLLECTION','A few<br><em>well-chosen words.</em>','Poetry, memories and writing shared on the original SLUGS website.')+section('Writing',writing))
write('people.html','Remembering friends',intro('PEOPLE & MEMORIES','Remembering<br><em>our friends.</em>','Tributes and obituaries from the original collection, with their authors and credits retained.')+section('Tributes & obituaries',people))
body=intro('CLUB HISTORY','A little history.<br><em>No rules.</em>','The Society of Lancaster University Graduate Speleologists: old enough to know better, and still sluggy.')+'''<section class="shell story-layout"><div class="story"><p class="eyebrow">CLAPDALE · 1976</p><h2>“There are no rules.”</h2><p>SLUGS was inaugurated in the warden’s room at Clapdale during the Bar Pot weekend in 1976. The constitution said, “there are no rules”.</p><p>And so it goes on: friends, caves, hills, shared weekends and a growing collection of memories.</p><h3>Thanks to the people who kept the stories</h3><p>Ian Edmundson, for creating the original website. Paul Simm, for hosting its pages. George Shaw and Sue Ianson, for creating—and finding again—the Tresviso 2000 website.</p><p>The photographs and writing remain credited to their original contributors.</p></div><figure><img src="assets/early-luss.jpg" alt="An early LUSS group on the fells, from John Sellers’s 1968–69 collection"><figcaption>Early LUSS · John Sellers’s collection, 1968–69.</figcaption></figure></section>'''+section('Club history & curiosities',history)+section('Further afield',links,subtitle='Historical external links may have moved or changed.')
write('history.html','Club history',body)
body=intro('SEARCH THE COLLECTION','Find a familiar<br><em>name or place.</em>','Search the titles, places, years and contributor notes in the photo, event, newsletter and writing indexes.')+'''<section class="shell search-page"><form class="search-form" role="search" id="archive-search"><label class="sr-only" for="q">Search titles, places and years</label><input id="q" name="q" type="search" placeholder="Try Tresviso, Borrowdale or 1976…"><button class="button" type="submit">Search →</button></form><p class="search-status" aria-live="polite" id="search-status"></p><div class="entries" id="search-results"></div><noscript><p>Search needs JavaScript. You can also browse the Photos, Events and Newsletters indexes using the navigation above.</p></noscript></section>'''
write('search.html','Search',body)
# Compatibility entry points to the new indexes.
for name,target in [('oddsand.html','history.html'),('about.html','history.html'),('Newsletters/index.html','../newsletters.html'),('Events/index.html','../events.html'),('Photos/index.html','../photos.html')]:
 p=OUT/name;p.parent.mkdir(exist_ok=True)
 p.write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={target}"><title>SLUGS archive</title><a href="{target}">Continue to the SLUGS archive</a></html>')
(OUT/'.htaccess').write_text('# Static SLUGS preview. No redirect to the previous hosting domain.\n')
(BASE/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
(BASE/'organisation-report.json').write_text(json.dumps({'catalog_entries':len(catalog),'events':len(events),'photo_and_film_collections':counts['photos'],'newsletters':len(news),'missing_original_pages':MISSING,'corrected_links':FIXES},indent=2))
print(json.dumps({'catalog_entries':len(catalog),'events':len(events),'photos':counts['photos'],'newsletters':len(news),'missing':MISSING},indent=2))
