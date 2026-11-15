#!/usr/bin/env python3
"""Opt-in Docker/SSH test with disposable keys, site and host-key storage.
Run directly: python3 tests/test_shell_integration.py
Unittest discovery does not launch Docker or contact the NAS.
"""
import pathlib,subprocess,tempfile,time,uuid,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def run(*args,**kw):return subprocess.run(args,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw).stdout

def main():
 for tool in ['docker','ssh','ssh-keygen']:
  if not shutil.which(tool):raise SystemExit('Required tool missing: '+tool)
 source=ROOT/'shell'
 if not source.exists():source=ROOT # packaged source
 name='slugs-shell-test-'+uuid.uuid4().hex[:10];image=name+':test'
 with tempfile.TemporaryDirectory(prefix='slugs-shell-test-') as temporary:
  temp=pathlib.Path(temporary);site=temp/'site';site.mkdir();site.chmod(0o777)
  ctx=temp/'build';ctx.mkdir();key=temp/'client'
  run('ssh-keygen','-q','-t','ed25519','-N','','-f',str(key))
  for file in ['Dockerfile','sshd_config','entrypoint.sh','.dockerignore']:shutil.copy(source/file,ctx/file)
  shutil.copy(str(key)+'.pub',ctx/'authorized_keys')
  try:
   run('docker','build','-t',image,str(ctx));print('PASS image build')
   run('docker','run','-d','--name',name,'--read-only','--cap-drop','ALL','--cap-add','SETUID','--cap-add','SETGID','--cap-add','SYS_CHROOT','--cap-add','CHOWN','--cap-add','FOWNER','--security-opt','no-new-privileges:true','--tmpfs','/run','--tmpfs','/tmp:mode=1777','--tmpfs','/home/slugs:uid=1026,gid=100,mode=700','--tmpfs','/hostkeys:mode=700','--mount','type=bind,source='+str(site)+',target=/volume1/web/slugs','-p','127.0.0.1::2222',image)
   port=run('docker','port',name,'2222/tcp').strip().rsplit(':',1)[1]
   for attempt in range(30):
    try:
     run('docker','exec',name,'/usr/sbin/sshd','-t');pub=run('docker','exec',name,'ssh-keygen','-y','-f','/hostkeys/ssh_host_ed25519_key').strip();break
    except subprocess.CalledProcessError:time.sleep(.2)
   else:raise AssertionError('SSH did not start')
   known=temp/'known_hosts';known.write_text('[127.0.0.1]:'+port+' '+pub+'\n')
   ssh=['ssh','-p',port,'-i',str(key),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(known),'-o','ConnectTimeout=5','slugs@127.0.0.1']
   for attempt in range(30):
    try:assert run(*ssh,'id -u').strip()=='1026';break
    except subprocess.CalledProcessError:time.sleep(.2)
   else:raise AssertionError('Key login failed')
   print('PASS key login and Unix identity')
   run(*ssh,'cd /volume1/web/slugs && printf test > test.txt && chmod 700 test.txt && test -x test.txt && cat test.txt')
   assert (site/'test.txt').read_text()=='test';print('PASS website read/write/execute')
   run(*ssh,'test ! -w /etc/passwd && test ! -e /var/run/docker.sock');print('PASS root filesystem write protection and no Docker socket')
   policy=run('docker','exec',name,'/usr/sbin/sshd','-T')
   for expected in ['passwordauthentication no','permitrootlogin no','authenticationmethods publickey','disableforwarding yes']:assert expected in policy.splitlines()
   badkey=temp/'unapproved';run('ssh-keygen','-q','-t','ed25519','-N','','-f',str(badkey))
   denied=ssh.copy();denied[denied.index(str(key))]=str(badkey)
   assert subprocess.run([*denied,'true'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0
   print('PASS auth/forwarding policy and unapproved key rejected')
  finally:
   subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   subprocess.run(['docker','image','rm',image],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
if __name__=='__main__':main()
