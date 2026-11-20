from pathlib import Path
import subprocess,hashlib,json,urllib.request,concurrent.futures,time
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--work-dir',type=Path,required=True);options=parser.parse_args();B=options.work_dir.resolve();stage=B/'staged';report=json.loads((B/'import-report.json').read_text());remote='/volume1/web/slugs/new/'
def ssh(command,**kw):return subprocess.run(['ssh','-o','BatchMode=yes','slugs-nas',command],check=True,capture_output=True,**kw)
assert ssh('cat '+remote+'events.html').stdout==(B/'events-before.html').read_bytes(),'Events changed; do not overwrite editor changes'
assert ssh('test ! -e '+remote+'blog-reports && echo clear').stdout.strip()==b'clear','Destination already exists; inspect before changing it'
subprocess.run(['rsync','-rlt','--checksum','--partial','--exclude=events.html',str(stage)+'/', 'slugs-nas:'+remote],check=True)
actual=ssh('cd '+remote+' && find blog-reports -type f -exec sha256sum {} \\;').stdout.decode().splitlines();hashes={line[66:]:line[:64] for line in actual}
expected={p.relative_to(stage).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in stage.rglob('*') if p.is_file() and p.name!='events.html'}
assert hashes==expected,'Uploaded report/media hashes do not match'
# Check again after upload, then replace only the Events page atomically.
assert ssh('cat '+remote+'events.html').stdout==(B/'events-before.html').read_bytes(),'Events changed during upload'
ssh('set -e; temporary=$(mktemp '+remote+'.events-blog-import.XXXXXX); cat > "$temporary"; chmod 644 "$temporary"; mv "$temporary" '+remote+'events.html',input=(stage/'events.html').read_bytes())
assert ssh('sha256sum '+remote+'events.html').stdout.decode().split()[0]==hashlib.sha256((stage/'events.html').read_bytes()).hexdigest()
print('Published and checksum-verified',len(expected),'new files and updated Events.',flush=True)
def check(path):
 url='https://slugs.granvillehouse.synology.me/new/'+path
 for attempt in range(3):
  try:
   method='GET' if path.endswith('.html') else 'HEAD'
   with urllib.request.urlopen(urllib.request.Request(url,method=method),timeout=35) as r:
    assert r.status==200
    if method=='GET':assert r.read()==(stage/path).read_bytes(),url
    return {'path':path,'status':r.status}
  except Exception:
   if attempt==2:raise
   time.sleep(1)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(check,sorted(expected)+['events.html']))
report['publication']={'nas_checksums_match':True,'public_checks':results,'original_site_untouched':True}
(B/'import-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS public checks:',len(results),'pages/images; original site untouched.',flush=True)
