from urllib.request import Request,urlopen
from urllib.parse import quote,urlsplit
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
base='https://slugs.granvillehouse.synology.me/new/'
p=Path(__file__).parent/'slugs-source'
records=json.loads((p/'catalog.json').read_text())
paths=['','photos.html','events.html','newsletters.html','writing.html','people.html','history.html','search.html?q=Tresviso','assets/site.css','assets/site.js','assets/patterdale.jpg']+[r['href']for r in records if not urlsplit(r['href']).scheme]
paths=list(dict.fromkeys(paths))
def check(path):
 try:
  with urlopen(Request(base+path,method='HEAD'),timeout=15) as r:return {'path':path,'status':r.status,'url':r.url}
 except Exception as e:return {'path':path,'error':str(e)}
with ThreadPoolExecutor(max_workers=5) as ex:results=list(ex.map(check,paths))
(p/'http-checks.json').write_text(json.dumps(results,indent=2))
print('Checked',len(results),'URLs. Failures:',[r for r in results if r.get('status')!=200])
