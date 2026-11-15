import os,tempfile,sys,re,io,json,unittest
from pathlib import Path
from PIL import Image
base=Path(tempfile.mkdtemp());root=base/'site';root.mkdir();(root/'new').mkdir();(root/'new/index.html').write_text('<!doctype html><html><head><title>Test</title></head><body><h1>Original</h1></body></html>');(root/'index.html').write_text('<html><body>Original root</body></html>');(root/'new/assets').mkdir();(root/'new/assets/test.css').write_text('body{color:green}');outside=base/'outside';outside.write_text('SECRET');(root/'new/link.txt').symlink_to(outside)
os.environ.update(WEB_ROOT=str(root),DATA_DIR=str(base/'data'),COOKIE_SECURE='0');sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'editor'))
import app as module
app=module.app;app.config['TESTING']=True
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.admin=app.test_client();cls.admin.get('/setup')
  with cls.admin.session_transaction() as s:cls.token=s['csrf']
  code=(base/'data/setup-token').read_text();r=cls.admin.post('/setup',data={'csrf':cls.token,'token':code,'username':'richard','password':'temporary-test-password-123'});assert r.status_code==302,r.data
  r=cls.admin.post('/login',data={'csrf':cls.token,'username':'richard','password':'temporary-test-password-123'});assert r.status_code==302
  with cls.admin.session_transaction() as s:cls.token=s['csrf']
  r=cls.admin.post('/api/users',json={'username':'editor','password':'temporary-editor-password-123','scope':'new','role':'editor'},headers={'X-CSRF-Token':cls.token});assert r.status_code==200,r.data
  cls.editor=app.test_client();cls.editor.get('/login')
  with cls.editor.session_transaction() as s:t=s['csrf']
  cls.editor.post('/login',data={'csrf':t,'username':'editor','password':'temporary-editor-password-123'})
  with cls.editor.session_transaction() as s:cls.et=s['csrf']
 def post(self,path,data,editor=False):return (self.editor if editor else self.admin).post(path,json=data,headers={'X-CSRF-Token':self.et if editor else self.token})
 def test_01_auth(self):
  c=app.test_client();self.assertEqual(c.get('/api/files').status_code,401);self.assertEqual(c.post('/api/save',json={}).status_code,403);self.assertEqual(self.admin.get('/setup').status_code,404)
 def test_02_scope_paths(self):
  self.assertEqual(self.editor.get('/api/read?path=index.html').status_code,403)
  for p in ['../outside','new/../index.html','new/link.txt','/new/.htaccess']:
   self.assertIn(self.admin.get('/api/read',query_string={'path':p}).status_code,[400,403])
  self.assertEqual(self.editor.get('/api/users').status_code,403)
 def test_03_save_conflict_restore(self):
  d=self.admin.get('/api/read?path=new/index.html').json;original=(root/'new/index.html').read_bytes();payload={**d,'content':d['content'].replace('Original','Changed')}
  self.assertEqual(self.post('/api/save',payload).status_code,200);self.assertEqual(self.post('/api/save',payload).status_code,409)
  rev=self.admin.get('/api/info?path=new/index.html').json['revision'];hist=self.admin.get('/api/history?path=new/index.html').json['items'];self.assertEqual(len(hist),1)
  r=self.post('/api/restore',{'id':hist[0]['id'],'revision':rev});self.assertEqual(r.status_code,200);self.assertEqual((root/'new/index.html').read_bytes(),original)
 def test_04_uploads(self):
  image=io.BytesIO();Image.new('RGB',(5,5),'green').save(image,format='PNG');data=image.getvalue()
  r=self.admin.post('/api/upload',data={'csrf':self.token,'folder':'new','file':(io.BytesIO(data),'photo.png')},content_type='multipart/form-data');self.assertEqual(r.status_code,200,r.data)
  r=self.admin.post('/api/upload',data={'csrf':self.token,'folder':'new','file':(io.BytesIO(b'%PDF-1.4 test'),'report.pdf')},content_type='multipart/form-data');self.assertEqual(r.status_code,200)
  r=self.admin.post('/api/upload',data={'csrf':self.token,'folder':'new','file':(io.BytesIO(b'not an image'),'bad.png')},content_type='multipart/form-data');self.assertEqual(r.status_code,400)
  r=self.admin.post('/api/upload',data={'csrf':self.token,'folder':'new','file':(io.BytesIO(b'<?php'),'bad.php')},content_type='multipart/form-data');self.assertEqual(r.status_code,400)
  r=self.admin.post('/api/upload',data={'csrf':self.token,'folder':'new','file':(io.BytesIO(data),'photo.png')},content_type='multipart/form-data');self.assertEqual(r.status_code,409)
  r=self.editor.post('/builder/upload.php',data={'csrf':self.et,'mediaPath':'/site/new/uploads','onlyFilename':'true','file':(io.BytesIO(data),'photo.png')},content_type='multipart/form-data');self.assertEqual(r.status_code,200,r.data)
 def test_05_templates_sandbox(self):
  r=self.admin.get('/builder/editor.html?page=new/index.html');self.assertEqual(r.status_code,200);self.assertIn(b'id="slugs-tools"',r.data);self.assertIn(b'window.slugsPage="new/index.html"',r.data)
  r=self.admin.get('/site/new/index.html');self.assertIn("script-src 'none'",r.headers['Content-Security-Policy']);self.assertIn('sandbox allow-same-origin',r.headers['Content-Security-Policy'])
 def test_06_csrf(self):
  self.assertEqual(self.admin.post('/api/folder',json={'path':'new/no'}).status_code,403)
  self.assertEqual(self.admin.post('/api/folder',json={'path':'new/no'},headers={'X-CSRF-Token':self.token,'Origin':'https://evil.example'}).status_code,403)
 def test_07_revocation(self):
  uid=next(x['id'] for x in self.admin.get('/api/users').json['items'] if x['username']=='editor');self.assertEqual(self.post('/api/users/'+str(uid),{'active':False}).status_code,200);self.assertEqual(self.editor.get('/api/files').status_code,401)
if __name__=='__main__':unittest.main(verbosity=2)
