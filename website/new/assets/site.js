'use strict';
(() => {
 const input = document.querySelector('[data-filter]');
 const year = document.querySelector('[data-year-filter]');
 const entries = [...document.querySelectorAll('.entry[data-search]')];
 const normal = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 function filter() {
  const terms = normal(input?.value || '').trim().split(/\s+/).filter(Boolean);
  let visible = 0;
  entries.forEach(entry => {
   const match = terms.every(term => normal(entry.dataset.search).includes(term)) && (!year?.value || entry.dataset.year === year.value);
   entry.hidden = !match; visible += Number(match);
  });
  document.querySelectorAll('.archive-section').forEach(section => {
   if (section.querySelector('.entry[data-search]')) {
    const count = [...section.querySelectorAll('.entry[data-search]')].filter(entry => !entry.hidden).length;
    section.hidden = count === 0;
    const heading = section.querySelector('.section-heading .eyebrow');
    if (heading) heading.textContent = `${count} ${count === 1 ? 'entry' : 'entries'}`;
   }
  });
  const count = document.querySelector('[data-filter-count]');
  if (count) count.textContent = `${visible} of ${entries.length} entries`;
  const empty = document.querySelector('[data-no-results]'); if (empty) empty.hidden = visible > 0;
 }
 if (input) { input.addEventListener('input',filter); year?.addEventListener('change',filter); filter(); }
 const form = document.querySelector('#archive-search');
 if (form) {
  const data = JSON.parse(document.querySelector('#archive-data').textContent);
  const q = document.querySelector('#q'); const results = document.querySelector('#search-results'); const status = document.querySelector('#search-status');
  function search(updateUrl) {
   const value = q.value.trim(); const terms = normal(value).split(/\s+/).filter(Boolean);
   results.replaceChildren();
   if (updateUrl) history.replaceState(null,'',location.pathname+(value ? '?q='+encodeURIComponent(value) : ''));
   if (!terms.length) {status.textContent = 'Try a place, a person or a year to explore the collection.';return;}
   const matches = data.filter(item => terms.every(term => normal([item.title,item.description,item.year,item.kind].join(' ')).includes(term)));
   status.textContent = `${matches.length} ${matches.length === 1 ? 'result' : 'results'} for “${value}”`;
   matches.forEach(item => {
    const article = document.createElement('article');article.className = 'entry';
    const content = document.createElement('div');const label = document.createElement('span');label.className='eyebrow';label.textContent=[item.kind,item.year].filter(Boolean).join(' · ');
    const h3 = document.createElement('h3');const link=document.createElement('a');link.href=item.href;link.textContent=item.title;h3.append(link);content.append(label,h3);
    if(item.description){const p=document.createElement('p');p.textContent=item.description;content.append(p);}
    const arrow=document.createElement('span');arrow.className='entry-arrow';arrow.textContent='Open →';arrow.setAttribute('aria-hidden','true');article.append(content,arrow);results.append(article);
   });
   if(!matches.length){const p=document.createElement('p');p.textContent='No matches found. Try a different spelling, a shorter place name or another year.';results.append(p);}
  }
  q.value=new URLSearchParams(location.search).get('q') || '';
  form.addEventListener('submit',event => {event.preventDefault();search(true);});
  q.addEventListener('input',() => search(true));search(false);
 }
})();
