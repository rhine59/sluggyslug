from pathlib import Path
import json,re,html,collections
B=Path(__file__).parent;s=(B/'events-before.html').read_text();feed=json.loads((B/'feed.json').read_text())['feed']['entry']
# Dates explicitly given in reports take precedence over Blogger publication dates.
info=[
('2025-12-19','Pre-Christmas meet at Beetham Cottage','19–21 December 2025'),
('2025-11-13','Bonfire party at Granny House','Report posted 13 November 2025'),
('2025-09-01','Fifty years of cave exploration below Tresviso','1–8 September 2025'),
('2025-05-08','Summer in Wasdale','8–9 May 2025'),
('2024-12-21','Pre-Christmas get-together at Beetham Cottage, Patterdale','Report posted 21 December 2024'),
('2024-11-07','Bonfire party at Granny House','7–10 November 2024'),
('2024-04-21','Tour of Ingleborough','21 April 2024'),
('2024-01-01','SLUGS New Year celebrations','30 December 2023–1 January 2024'),
('2023-12-13','Christmas meet, Borrowdale','13–14 December 2023'),
('2023-09-30','A trip to the seaside: Blackpool cycling, fish and chips','30 September 2023'),
('2023-09-15','Summer Slither 2023','Report posted 15 September 2023'),
('2023-07-01','SLUGS meet, Wasdale','1–2 July 2023'),
('2023-02-10',"Ski ’23, Alpe d’Huez",'Report posted 10 February 2023'),
('2022-12-31','Christmas get-together, Buttermere','Report posted 31 December 2022'),
('2022-11-15','Bonfire 2022 at Granny House','Report posted 15 November 2022'),
('2022-09-09','Riverside Cottage, Horton in Ribblesdale','9–11 September 2022'),
('2022-07-30','Summer Slither at Granny House','Report posted 30 July 2022'),
('2022-07-29','RHS Gardens, Bridgewater Hall','Delayed report posted 29 July 2022'),
('2022-07-11','A Rum Do: Isle of Rum','Report posted 11 July 2022'),
('2022-04-23','A slither up Great Whernside','23 April 2022'),
('2022-04-06','SLUGS biking around Pen-y-ghent','Report posted 6 April 2022'),
('2021-12-27','Weekend at Raw Head Cottage, Langdale','Report posted 27 December 2021'),
('2021-10-16','Tour of Howgills: a re-cycle event','16 October 2021'),
('2021-09-18','SLUGS weekend at Loftburn','18–19 September 2021'),
('2021-08-14','Tour de Howgills','14 August 2021'),
('2021-07-24','Summer Slither at Bell Busk','24–25 July 2021'),
('2021-06-26','SLUGS Tour de Whernside','26 June 2021'),
('2021-05-16','Easegill, Crag Hill and Gragareth','16 May 2021')]
assert len(info)==len(feed)==28
# Remove the two separately featured paragraphs; retain existing chronological entries.
s=re.sub(r'<p class="lede"><a class="text-link" href="https://slugsreports.blogspot.com/">.*?</p>','',s,count=1,flags=re.S)
s=re.sub(r'<p class="lede"><strong>Rawhead Christmas meets:</strong>.*?</p>','',s,count=1,flags=re.S)
needle='Browse the club reports by year, or search for a place or event.</p>'
s=s.replace(needle,needle+'<p class="fine">Includes reports from the SLUGS Reports blog. Newest first; event dates are used where stated, otherwise the publication date is shown.</p>')
groups=collections.defaultdict(list);catalog=[]
for e,(date,title,label) in zip(feed,info):
 url=next(x['href'] for x in e['link'] if x['rel']=='alternate');year=date[:4];esc=lambda v:html.escape(v,quote=True)
 groups[year].append((date,f'<article class="entry" data-search="{esc(title+" "+label+" SLUGS Reports blog Christmas Rawhead" if "Raw Head" in title else title+" "+label+" SLUGS Reports blog")}" data-year="{year}"><div><span class="eyebrow">{esc(label)} · Blog report</span><h3><a href="{esc(url)}">{esc(title)}</a></h3></div><span class="entry-arrow" aria-hidden="true">Read report ↗</span></article>'))
 catalog.append(dict(title=title,href=url,date=date,date_label=label,year=year))
sections=''
for year in sorted(groups,reverse=True):
 entries=sorted(groups[year],key=lambda x:x[0],reverse=True)
 sections+=f'<section class="archive-section shell"><div class="section-heading"><div><p class="eyebrow">{len(entries)} entries</p><h2>{year}</h2></div></div><div class="entries">'+''.join(x[1] for x in entries)+'</div></section>'
assert s.count('<section class="archive-section shell">')>0
s=s.replace('<section class="archive-section shell">',sections+'<section class="archive-section shell">',1)
s=s.replace('<option value="">All years</option>','<option value="">All years</option>'+''.join('<option>'+y+'</option>' for y in sorted(groups,reverse=True)))
assert len(re.findall(r'<article class="entry"',s))==100
assert s.count('href="https://slugsreports.blogspot.com/')==28
(B/'events.html').write_text(s);(B/'added-reports.json').write_text(json.dumps(catalog,indent=2))
print('100 entries: 72 existing + 28 blog reports, grouped newest first')
