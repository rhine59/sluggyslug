#!/usr/bin/env python3
"""Read-only public deployment checks. Never skips certificate validation."""
import argparse,json,sys,urllib.request,urllib.error
p=argparse.ArgumentParser();p.add_argument('--url',default='https://slugs-editor.granvillehouse.synology.me');a=p.parse_args()
base=a.url.rstrip('/')
if not base.startswith('https://'):p.error('Use the production HTTPS address.')
failed=[]
def fetch(path):
 try:
  with urllib.request.urlopen(base+path,timeout=20) as r:return r.status,r.read(),r.headers
 except urllib.error.HTTPError as e:return e.code,e.read(),e.headers
checks=[('/health',200),('/api/files',401)]
for path,expected in checks:
 try:
  status,body,headers=fetch(path)
  assert status==expected,f'expected {expected}, received {status}'
  if path=='/health':assert json.loads(body).get('status')=='ok','unhealthy response'
  print('PASS',path,status)
 except Exception as e:failed.append(path);print('FAIL',path,str(e))
try:
 status,body,headers=fetch('/')
 assert status==200,f'home/sign-in/setup returned {status}'
 print('PASS home/sign-in/setup reachable over verified HTTPS')
except Exception as e:failed.append('/');print('FAIL /',str(e))
print('These checks do not create accounts, save pages, upload files or prove editor permissions. Complete the manual acceptance checklist.')
sys.exit(bool(failed))
