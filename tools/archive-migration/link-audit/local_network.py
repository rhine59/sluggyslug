from pathlib import Path
from urllib.parse import quote
import json,urllib.request,urllib.error,concurrent.futures
B=Path(__file__).parent;r=json.loads((B/'after.json').read_text());paths=sorted({x['target'] for x in r['valid']});out=[]
def check(p):
 url='https://slugs.granvillehouse.synology.me/new/'+quote(p,safe='/')
 try:
  with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=20) as h:return dict(path=p,status=h.status)
 except urllib.error.HTTPError as e:return dict(path=p,status=e.code)
 except Exception as e:return dict(path=p,status=0,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for f in concurrent.futures.as_completed([pool.submit(check,p) for p in paths]):
  out.append(f.result())
  if len(out)%200==0:(B/'local-network.json').write_text(json.dumps(out));print(len(out),'/',len(paths),flush=True)
(B/'local-network.json').write_text(json.dumps(out));print('DONE',len(out),flush=True)
