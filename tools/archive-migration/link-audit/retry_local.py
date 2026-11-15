from pathlib import Path
import json,urllib.request,urllib.error,concurrent.futures
from urllib.parse import quote
B=Path(__file__).parent
import time
while 'DONE' not in (B/'local-network.log').read_text():time.sleep(1)
r=json.loads((B/'local-network.json').read_text());paths={x['path'] for x in r if x['status']!=200};paths|={p.relative_to(B/'fixed').as_posix() for p in (B/'fixed').rglob('*') if p.is_file()};paths.add('../')
def test(p):
 u='https://slugs.granvillehouse.synology.me/new/'+quote(p,safe='/')
 try:
  with urllib.request.urlopen(urllib.request.Request(u,method='HEAD'),timeout=25) as h:return dict(path=p,status=h.status)
 except urllib.error.HTTPError as e:return dict(path=p,status=e.code)
 except Exception as e:return dict(path=p,status=0,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(test,sorted(paths)))
(B/'local-retry.json').write_text(json.dumps(out,indent=2));print('DONE',len(out),'failures',sum(x['status']!=200 for x in out),flush=True)
