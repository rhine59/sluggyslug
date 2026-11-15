from pathlib import Path
import json,urllib.request,urllib.error,concurrent.futures
B=Path(__file__).parent;r=json.loads((B/'network.json').read_text())
def get(x):
 try:
  with urllib.request.urlopen(urllib.request.Request(x['url'],headers={'User-Agent':'Mozilla/5.0'}),timeout=12) as h:
   h.read(1024);return dict(url=x['url'],status=h.status,final=h.url)
 except urllib.error.HTTPError as e:return dict(url=x['url'],status=e.code,final=e.url)
 except Exception as e:return dict(url=x['url'],status=0,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:out=list(pool.map(get,[x for x in r if x['status'] in [404,410]]))
(B/'external-get-confirmation.json').write_text(json.dumps(out,indent=2));print('GET confirmed',len(out),'recovered',[x for x in out if x['status']==200],flush=True)
