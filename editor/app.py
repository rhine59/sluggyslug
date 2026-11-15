import os,re,secrets,sqlite3,time,hashlib,json,io,tempfile,fcntl,mimetypes
from pathlib import Path,PurePosixPath
from functools import wraps
from datetime import timedelta
from urllib.parse import quote
from flask import Flask,request,session,g,render_template,jsonify,redirect,url_for,send_file,abort
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
from PIL import Image,UnidentifiedImageError

ROOT=Path(os.environ.get('WEB_ROOT','/site')).resolve();DATA=Path(os.environ.get('DATA_DIR','/data')).resolve();DATA.mkdir(parents=True,exist_ok=True)
for d in ['backups','locks']:(DATA/d).mkdir(exist_ok=True)
def secret_file(name):
 p=DATA/name
 try:
  fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(fd,'w') as f:f.write(secrets.token_urlsafe(36))
 except FileExistsError:pass
 return p.read_text().strip()
app=Flask(__name__);app.secret_key=secret_file('session-key');secret_file('setup-token')
app.config.update(MAX_CONTENT_LENGTH=105*1024*1024,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Strict',SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE','1')=='1',PERMANENT_SESSION_LIFETIME=timedelta(hours=8))
if os.environ.get('TRUST_PROXY','0')=='1':app.wsgi_app=ProxyFix(app.wsgi_app,x_for=1,x_proto=1,x_host=1,x_prefix=1)
TEXT={'.html','.htm','.css','.js','.json','.txt','.md','.xml','.svg'}
UPLOAD={'.jpg','.jpeg','.png','.gif','.webp','.avif','.ico','.pdf','.txt','.md','.doc','.docx','.xls','.xlsx','.ppt','.pptx','.zip','.mp4','.webm','.mov','.mp3','.wav','.ogg'}
IMAGES={'.jpg','.jpeg','.png','.gif','.webp','.avif','.ico'}
def db():
 if 'db' not in g:
  g.db=sqlite3.connect(DATA/'editor.sqlite',timeout=20);g.db.row_factory=sqlite3.Row;g.db.execute('PRAGMA foreign_keys=ON')
 return g.db
@app.teardown_appcontext
def close_db(error):
 c=g.pop('db',None)
 if c:c.close()
with app.app_context():
 db().executescript('''PRAGMA journal_mode=WAL;
 CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE NOT NULL,password TEXT NOT NULL,role TEXT NOT NULL,scope TEXT NOT NULL,active INTEGER NOT NULL DEFAULT 1,version INTEGER NOT NULL DEFAULT 1);
 CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id INTEGER,version INTEGER,expires REAL);
 CREATE TABLE IF NOT EXISTS attempts(bucket TEXT,at REAL);
 CREATE TABLE IF NOT EXISTS revisions(id INTEGER PRIMARY KEY,path TEXT NOT NULL,backup TEXT NOT NULL,by_user TEXT NOT NULL,at REAL NOT NULL,action TEXT NOT NULL,sha TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,at REAL NOT NULL,username TEXT,action TEXT,path TEXT);
 ''');db().commit()
def clean_path(raw,allow_empty=False):
 if not isinstance(raw,str) or '\\' in raw or '\x00' in raw or any(ord(c)<32 for c in raw):abort(400,'Invalid path')
 raw=raw.strip('/')
 if not raw:
  if allow_empty:return ''
  abort(400,'Choose a file')
 parts=raw.split('/')
 if any(p in ['.','..',''] or p.startswith('.') for p in parts):abort(400,'Hidden and parent paths are not allowed')
 return '/'.join(parts)
def resolve(raw,write=False,allow_empty=False):
 rel=clean_path(raw,allow_empty);p=ROOT/rel
 if not p.resolve().is_relative_to(ROOT):abort(403,'Path outside website')
 current=ROOT
 for bit in PurePosixPath(rel).parts:
  current=current/bit
  if current.is_symlink():abort(403,'Symbolic links are not editable')
 if write:check_scope(rel)
 return p,rel
def check_scope(rel):
 scope=g.user['scope']
 if scope and rel!=scope and not rel.startswith(scope+'/'):abort(403,'Your account cannot edit this folder')
def audit(action,path=''):
 db().execute('INSERT INTO audit(at,username,action,path) VALUES(?,?,?,?)',(time.time(),g.user['username'] if getattr(g,'user',None) else 'anonymous',action,path));db().commit()
def csrf():
 if 'csrf' not in session:session['csrf']=secrets.token_hex(32)
 return session['csrf']
app.jinja_env.globals.update(csrf=csrf)
@app.before_request
def protect():
 g.user=None
 sid=session.get('sid')
 if sid:
  row=db().execute('SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token=? AND s.expires>? AND s.version=u.version AND u.active=1',(hashlib.sha256(sid.encode()).hexdigest(),time.time())).fetchone();g.user=row
 if request.method not in ['GET','HEAD','OPTIONS']:
  supplied=request.headers.get('X-CSRF-Token') or request.form.get('csrf','')
  if not secrets.compare_digest(str(supplied),session.get('csrf','!')):abort(403,'Session expired. Reload and sign in again.')
  origin=request.headers.get('Origin')
  if origin and origin.rstrip('/')!=request.host_url.rstrip('/'):abort(403,'Origin mismatch')
@app.after_request
def headers(response):
 response.headers['X-Content-Type-Options']='nosniff';response.headers['Referrer-Policy']='same-origin';response.headers['Cache-Control']='no-store';response.headers['X-Frame-Options']='SAMEORIGIN'
 return response
@app.errorhandler(HTTPException)
def error(e):
 if request.path.startswith('/api/') or request.path.startswith('/builder/') and request.method=='POST':return jsonify(error=e.description),e.code
 return render_template('error.html',message=e.description),e.code
@app.errorhandler(OSError)
def io_error(e):
 app.logger.exception('File operation failed');return jsonify(error='The file operation failed. Check space and folder permissions; the existing file was retained.'),500

def login_required(fn):
 @wraps(fn)
 def wrapped(*a,**kw):
  if not g.user:
   if request.path.startswith('/api/'):abort(401,'Please sign in')
   return redirect(url_for('login'))
  return fn(*a,**kw)
 return wrapped
def admin_required(fn):
 @wraps(fn)
 @login_required
 def wrapped(*a,**kw):
  if g.user['role']!='admin':abort(403,'Administrator account required')
  return fn(*a,**kw)
 return wrapped

def rate_limit(bucket):
 now=time.time();db().execute('DELETE FROM attempts WHERE at<?',(now-900,))
 if db().execute('SELECT count(*) FROM attempts WHERE bucket=?',(bucket,)).fetchone()[0]>=8:abort(429,'Too many attempts. Try again in 15 minutes.')
 db().execute('INSERT INTO attempts VALUES(?,?)',(bucket,now));db().commit()
def validate_user(username,password,role,scope):
 if not re.fullmatch('[A-Za-z0-9_.-]{3,40}',username):abort(400,'Username: 3–40 letters, numbers, dots, dashes or underscores')
 if len(password)<14 or len(password)>256:abort(400,'Use a password of 14–256 characters')
 if role not in ['admin','editor']:abort(400,'Invalid account role')
 scope=clean_path(scope,True)
 if scope and not (ROOT/scope).is_dir():abort(400,'The permitted folder must already exist')
 return scope
@app.route('/setup',methods=['GET','POST'])
def setup():
 if db().execute('SELECT count(*) FROM users').fetchone()[0]:abort(404)
 if request.method=='POST':
  rate_limit('setup:'+request.remote_addr)
  if not secrets.compare_digest(request.form.get('token',''),(DATA/'setup-token').read_text().strip()):abort(403,'Incorrect setup code')
  name=request.form.get('username','').strip();pw=request.form.get('password','');validate_user(name,pw,'admin','')
  with open(DATA/'setup.lock','a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   if db().execute('SELECT count(*) FROM users').fetchone()[0]:abort(409,'Setup has already completed')
   db().execute('INSERT INTO users(username,password,role,scope) VALUES(?,?,?,?)',(name,generate_password_hash(pw), 'admin',''));db().commit()
  (DATA/'setup-token').unlink(missing_ok=True)
  return redirect(url_for('login'))
 return render_template('setup.html')
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  name=request.form.get('username','').strip();rate_limit('ip:'+request.remote_addr);rate_limit('user:'+name.lower())
  u=db().execute('SELECT * FROM users WHERE username=? AND active=1',(name,)).fetchone()
  if not u or not check_password_hash(u['password'],request.form.get('password','')):return render_template('login.html',error='Username or password incorrect'),401
  session.clear();session.permanent=True;sid=secrets.token_hex(32);session['sid']=sid;csrf()
  db().execute('INSERT INTO sessions VALUES(?,?,?,?)',(hashlib.sha256(sid.encode()).hexdigest(),u['id'],u['version'],time.time()+28800));db().execute('DELETE FROM attempts WHERE bucket=?',('user:'+name.lower(),));db().commit();g.user=u;audit('login')
  return redirect(url_for('home'))
 return render_template('login.html')
@app.post('/logout')
@login_required
def logout():
 db().execute('DELETE FROM sessions WHERE token=?',(hashlib.sha256(session.get('sid','').encode()).hexdigest(),));db().commit();session.clear();return redirect(url_for('login'))
@app.get('/health')
def health():return jsonify(status='ok')
@app.get('/')
@login_required
def home():return render_template('home.html')
@app.get('/api/files')
@login_required
def files():
 p,rel=resolve(request.args.get('path',g.user['scope']),allow_empty=True);check_scope(rel)
 if not p.is_dir():abort(404,'Folder not found')
 items=[]
 for f in sorted(p.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold())):
  if f.name.startswith('.') or f.is_symlink():continue
  items.append(dict(name=f.name,path=f.relative_to(ROOT).as_posix(),directory=f.is_dir(),size=f.stat().st_size if f.is_file() else 0,visual=f.suffix.lower() in ['.html','.htm'],text=f.suffix.lower() in TEXT))
 return jsonify(path=rel,scope=g.user['scope'],items=items)
@app.get('/api/read')
@login_required
def read():
 p,rel=resolve(request.args.get('path',''),write=True)
 if not p.is_file() or p.suffix.lower() not in TEXT:abort(400,'Choose an editable text file')
 data=p.read_bytes()
 if len(data)>4*1024*1024:abort(413,'Text files must be below 4 MB')
 try:text=data.decode('utf-8');encoding='utf-8'
 except UnicodeDecodeError:text=data.decode('cp1252');encoding='cp1252'
 return jsonify(path=rel,content=text,encoding=encoding,revision=hashlib.sha256(data).hexdigest())
def locked_write(rel,data,expected,action):
 p,rel=resolve(rel,write=True)
 if len(data)>100*1024*1024:abort(413,'Files must be below 100 MB')
 with open(DATA/'locks'/hashlib.sha256(rel.encode()).hexdigest(),'a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  old=p.read_bytes() if p.exists() else None
  current=hashlib.sha256(old).hexdigest() if old is not None else 'missing'
  if expected!=current:abort(409,'This file changed since you opened it. Your changes have not overwritten it. Reload before saving.')
  if old is not None:
   backup=secrets.token_hex(20);out=DATA/'backups'/backup
   with open(out,'xb') as f:f.write(old);f.flush();os.fsync(f.fileno())
   db().execute('INSERT INTO revisions(path,backup,by_user,at,action,sha) VALUES(?,?,?,?,?,?)',(rel,backup,g.user['username'],time.time(),action,current));db().commit()
  if not p.parent.is_dir():abort(400,'Destination folder does not exist')
  fd,tmp=tempfile.mkstemp(prefix='.slugs-editor-',dir=p.parent)
  try:
   with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
   os.chmod(tmp,(p.stat().st_mode & 0o777) if p.exists() else 0o644);os.replace(tmp,p)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
 audit(action,rel)
 return hashlib.sha256(data).hexdigest()
@app.get('/api/info')
@login_required
def info():
 p,rel=resolve(request.args.get('path',''),write=True)
 if not p.is_file():abort(404,'File not found')
 digest=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
 return jsonify(path=rel,revision=digest.hexdigest(),size=p.stat().st_size)
@app.post('/api/save')
@login_required
def save():
 payload=request.get_json() or {};p,rel=resolve(payload.get('path',''),write=True)
 if p.suffix.lower() not in TEXT:abort(400,'File type cannot be edited')
 content=payload.get('content')
 if not isinstance(content,str):abort(400,'Missing text')
 if p.suffix.lower() in ['.htm','.html'] and (not content.strip() or '<html' not in content.lower()):abort(400,'A complete HTML document is required')
 encoding=payload.get('encoding','utf-8')
 if encoding not in ['utf-8','cp1252']:abort(400,'Invalid encoding')
 try:data=content.encode(encoding)
 except UnicodeEncodeError:abort(400,'This old page cannot store one of the characters you entered. Use the source editor to convert its charset to UTF-8 first.')
 digest=locked_write(rel,data,payload.get('revision'), 'save')
 return jsonify(revision=digest,message='Saved. The previous version is available in History.')
@app.post('/api/folder')
@login_required
def folder():
 x=request.get_json() or {};p,rel=resolve(x.get('path',''),write=True)
 if not p.parent.is_dir():abort(400,'Parent folder does not exist')
 try:p.mkdir()
 except FileExistsError:abort(409,'Folder already exists')
 audit('create-folder',rel);return jsonify(path=rel)
@app.post('/api/upload')
@login_required
def upload():
 f=request.files.get('file');folder=request.form.get('folder','');name=f.filename if f else ''
 if not name or '/' in name or '\\' in name or name.startswith('.'):abort(400,'Invalid filename')
 p,rel=resolve((folder+'/' if folder else '')+name,write=True)
 ext=p.suffix.lower()
 if ext not in UPLOAD:abort(400,'This file type is not permitted. Upload images, documents, ZIP archives, audio or video; executable files are blocked.')
 data=f.read(100*1024*1024+1)
 if len(data)>100*1024*1024:abort(413,'Maximum upload size: 100 MB')
 if ext in IMAGES:
  try:
   with Image.open(io.BytesIO(data)) as image:image.verify()
  except (OSError,ValueError,UnidentifiedImageError):abort(400,'This file is not a valid supported image')
 revision=locked_write(rel,data,request.form.get('revision','missing'),'upload')
 return jsonify(path=rel,url='/'+quote(rel,safe='/'),revision=revision)
@app.get('/api/history')
@login_required
def history():
 p,rel=resolve(request.args.get('path',''),write=True)
 rows=db().execute('SELECT id,by_user,at,action,sha FROM revisions WHERE path=? ORDER BY id DESC LIMIT 100',(rel,)).fetchall();return jsonify(items=[dict(r) for r in rows])
@app.post('/api/restore')
@login_required
def restore():
 x=request.get_json() or {};r=db().execute('SELECT * FROM revisions WHERE id=?',(x.get('id'),)).fetchone()
 if not r:abort(404,'Backup not found')
 resolve(r['path'],write=True);data=(DATA/'backups'/r['backup']).read_bytes()
 return jsonify(revision=locked_write(r['path'],data,x.get('revision'),'restore'))
@app.get('/api/users')
@admin_required
def users():return jsonify(items=[dict(r) for r in db().execute('SELECT id,username,role,scope,active FROM users ORDER BY username')])
@app.post('/api/users')
@admin_required
def add_user():
 x=request.get_json() or {};name=x.get('username','').strip();password=x.get('password','');role=x.get('role','editor');scope=validate_user(name,password,role,x.get('scope','new'))
 try:db().execute('INSERT INTO users(username,password,role,scope) VALUES(?,?,?,?)',(name,generate_password_hash(password),role,scope));db().commit()
 except sqlite3.IntegrityError:abort(409,'Username already exists')
 audit('create-user',name);return jsonify(message='Account created')
@app.post('/api/users/<int:uid>')
@admin_required
def change_user(uid):
 x=request.get_json() or {};u=db().execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
 if not u:abort(404)
 if uid==g.user['id']:abort(400,'Use another administrator to change this account')
 active=int(bool(x.get('active',u['active'])));role=x.get('role',u['role']);scope=clean_path(x.get('scope',u['scope']),True)
 if role not in ['admin','editor']:abort(400)
 if scope and not (ROOT/scope).is_dir():abort(400,'Folder does not exist')
 password=x.get('password');hashed=u['password']
 if password:validate_user(u['username'],password,role,scope);hashed=generate_password_hash(password)
 db().execute('UPDATE users SET active=?,role=?,scope=?,password=?,version=version+1 WHERE id=?',(active,role,scope,hashed,uid));db().commit();audit('update-user',u['username']);return jsonify(message='Account updated; previous sessions ended')
@app.get('/api/audit')
@admin_required
def activity():return jsonify(items=[dict(r) for r in db().execute('SELECT at,username,action,path FROM audit ORDER BY id DESC LIMIT 200')])
@app.get('/builder/editor.html')
@login_required
def builder():
 p,rel=resolve(request.args.get('page','new/index.html'),write=True)
 if p.suffix.lower() not in ['.html','.htm'] or not p.is_file():abort(400,'Choose an HTML page')
 return render_template('builder.html',page=rel)

@app.get('/builder/scan.php')
@login_required
def media_scan():
 raw=request.args.get('mediaPath','/site/new/uploads').removeprefix('/site/')
 p,rel=resolve(raw,write=True)
 items=[]
 if p.is_dir():
  for f in sorted(p.iterdir()):
   if f.is_file() and not f.is_symlink() and f.suffix.lower() in UPLOAD:
    items.append(dict(name=f.name,type='file',path='/'+f.name,size=f.stat().st_size))
 return jsonify(name='',type='folder',path='',items=items)
@app.post('/builder/upload.php')
@login_required
def media_upload():
 f=request.files.get('file')
 if not f or not f.filename or '/' in f.filename or '\\' in f.filename or f.filename.startswith('.'):abort(400,'Invalid filename')
 raw=request.form.get('mediaPath','/site/new/uploads').removeprefix('/site/').strip('/')
 folder,rel=resolve(raw,write=True)
 if not folder.exists():folder.mkdir()
 # Always use a unique name: the page builder never silently replaces an existing image.
 ext=Path(f.filename).suffix.lower()
 if ext not in IMAGES:abort(400,'Choose a JPEG, PNG, GIF, WebP, AVIF or icon file')
 data=f.read(20*1024*1024+1)
 if len(data)>20*1024*1024:abort(413,'Builder photos must be below 20 MB; larger files can be uploaded from Files & uploads')
 try:
  with Image.open(io.BytesIO(data)) as image:image.verify()
 except (OSError,ValueError,UnidentifiedImageError):abort(400,'Invalid image')
 name=re.sub('[^A-Za-z0-9_-]','-',Path(f.filename).stem)[:80]+'-'+secrets.token_hex(5)+ext
 locked_write(rel+'/'+name,data,'missing','upload')
 return name if request.form.get('onlyFilename') else '/site/'+quote(rel+'/'+name,safe='/')

@app.get('/builder/<path:name>')
@login_required
def builder_asset(name):
 # Serve only the vendored front-end, never demo server endpoints.
 p=Path(app.root_path)/'vendor'/name
 if name.split('/')[0] not in ['css','js','libs','fonts','img','html','resources'] or not p.resolve().is_relative_to((Path(app.root_path)/'vendor').resolve()) or p.suffix.lower() in ['.php','.map']:abort(404)
 if not p.is_file():abort(404)
 return send_file(p)
@app.route('/site/',defaults={'name':''})
@app.route('/site/<path:name>')
@app.route('/<path:name>')
@login_required
def site_file(name):
 p,rel=resolve(name,allow_empty=True)
 if p.is_dir():
  for ix in ['index.html','index.htm','INDEX.HTML','INDEX.HTM']:
   if (p/ix).is_file():p=p/ix;break
 if not p.is_file() or p.suffix.lower() not in TEXT|UPLOAD:abort(404)
 response=send_file(p,conditional=True)
 response.headers['Content-Security-Policy']="sandbox allow-same-origin; script-src 'none'; object-src 'none'; frame-src 'none'; connect-src 'none'; form-action 'none'"
 return response
if __name__=='__main__':
 from waitress import serve
 serve(app,host='0.0.0.0',port=int(os.environ.get('PORT','8080')),threads=6,max_request_body_size=105*1024*1024,clear_untrusted_proxy_headers=False)
