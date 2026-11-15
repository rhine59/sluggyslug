from pathlib import Path
import json,urllib.request,urllib.error,concurrent.futures,time
B=Path(__file__).parent;r=json.loads((B/'audit.json').read_text());urls=sorted({x['url'] for x in r['external'] if x['url'].startswith(('http://','https://'))})
def test(u):
 def req(url,method):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,method=method,headers={'User-Agent':'Mozilla/5.0 (SLUGS link check)'}),timeout=9) as h:return dict(url=u,status=h.status,final=h.url)
  except urllib.error.HTTPError as e:return dict(url=u,status=e.code,final=e.url)
  except Exception as e:return dict(url=u,status=0,error=str(e))
 a=req(u,'HEAD')
 if a['status'] in [403,405,501]:a=req(u,'GET')
 if (not a['status'] or a['status']>=400) and u.startswith('http://'):
  b=req('https://'+u[7:],'HEAD')
  if 200<=b['status']<400:a=b
 return a
out=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
 for x in pool.map(test,urls):
  out.append(x);(B/'network.json').write_text(json.dumps(out,indent=2))
  if len(out)%40==0:print(len(out),'/',len(urls),flush=True)
print('DONE',len(out),flush=True)
