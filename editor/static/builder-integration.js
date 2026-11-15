'use strict';
(async()=>{
 const page=window.slugsPage,csrf=window.slugsCsrf,note=document.querySelector('#slugs-save-note');
 const nativeFetch=window.fetch.bind(window);
 // The upstream image uploader uses fetch; attach our token only to same-origin mutations.
 window.fetch=(input,opts={})=>{const url=new URL(typeof input==='string'?input:input.url,location.href);if(url.origin===location.origin&&opts.method&&opts.method.toUpperCase()!=='GET'){opts={...opts,headers:new Headers(opts.headers||{})};opts.headers.set('X-CSRF-Token',csrf)}return nativeFetch(input,opts)};
 async function api(url,body){const r=await fetch(url,body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{});const d=await r.json();if(!r.ok)throw Error(d.error||'Request failed');return d}
 try{
  window.addEventListener('Vvveb.iframe.loaded',e=>{note.textContent=page;e.detail.addEventListener('input',()=>{note.textContent='Unsaved changes';document.querySelectorAll('#top-panel .save-btn').forEach(b=>b.removeAttribute('disabled'))});});
  const original=await api('/api/read?path='+encodeURIComponent(page));let revision=original.revision;
  window.mediaPath='/site/'+(page.includes('/')?page.slice(0,page.lastIndexOf('/'))+'/':'')+'uploads';
  window.mediaScanUrl='/builder/scan.php?mediaPath='+encodeURIComponent(window.mediaPath);
  Vvveb.Builder.save=async function(data,url,success,error,done){
   try{
    // Image selection uses editor-only URLs. Public files use the real web-root path.
    if(Vvveb.WysiwygEditor.isActive)Vvveb.WysiwygEditor.destroy(Vvveb.WysiwygEditor.element);
    let html=this.getHtml(false).replace(/((?:src|href|poster|background)\s*=\s*["'])\/site\//gi,'$1/').replace(/url\(["']?\/site\//gi,'url(/');
    const saved=await api('/api/save',{path:page,revision,encoding:original.encoding,content:html});revision=saved.revision;note.textContent='Saved · backup kept';document.querySelectorAll('#top-panel .save-btn').forEach(b=>b.setAttribute('disabled','true'));if(success)success(saved.message);Vvveb.Undo.reset();
   }catch(e){note.textContent='Not saved';alert(e.message);if(error)error({statusText:e.message})}
   finally{if(done)done()}
  };
  const pages={current:{name:'current',file:page,filename:page.split('/').pop(),url:'/site/'+page.split('/').map(encodeURIComponent).join('/'),title:page}};
  Vvveb.Builder.init(pages.current.url,()=>{note.textContent=page;});
  Vvveb.Gui.init();Vvveb.FileManager.init();Vvveb.SectionList.init();Vvveb.StyleList.init();Vvveb.TreeList.init();Vvveb.Breadcrumb.init();Vvveb.CssEditor.init();Vvveb.FileManager.addPages(pages);Vvveb.FileManager.loadPage('current');Vvveb.Gui.toggleRightColumn(false);
  window.addEventListener('beforeunload',e=>{if(Vvveb.Undo.hasChanges?.()){e.preventDefault();e.returnValue=''}});
 }catch(e){note.textContent=e.message;alert(e.message)}
})();
