#!/usr/bin/env python3
"""Capture public LABG pages/assets only; no authentication or form submission."""
import mimetypes, subprocess, concurrent.futures, hashlib, html, json, re, time, urllib.request, urllib.parse
from pathlib import Path
BASE='https://labrewersguild.org/'
ROOT=Path(__file__).resolve().parents[1]/'archive'
ROOT.mkdir(parents=True,exist_ok=True)
prior={r['url']:r for r in json.loads((ROOT/'manifest.json').read_text())} if (ROOT/'manifest.json').exists() else {}
seen=set(); records=[]; queue={BASE,BASE+'robots.txt',BASE+'wp-sitemap.xml',BASE+'sitemap_index.xml',BASE+'wp-json/wp/v2/types'}
for n in range(2,9): queue.add(BASE+'wp-json/wp/v2/tribe_events?per_page=100&page='+str(n))
for n in range(2,7): queue.add(BASE+'wp-json/wp/v2/media?per_page=100&page='+str(n))
queue.add(BASE+'wp-json/wp/v2/media?per_page=100&page=4&_fields=id,date,date_gmt,slug,type,link,title,source_url,mime_type,alt_text,caption,description,parent')
for t in ['pages','posts','media']:
 queue.add(BASE+'wp-json/wp/v2/'+t+'?per_page=100&page=1')
queue.update(u for u,r in prior.items() if r.get('status')==200)
if (ROOT/'pending.json').exists():queue.update(json.loads((ROOT/'pending.json').read_text()))
def get(url):
 if url in prior and prior[url].get('status')==200:
  old=ROOT/prior[url]['file']
  if old.exists():
   hp=old.with_name(old.name+'.response.json')
   return prior[url],old.read_bytes(),json.loads(hp.read_text()) if hp.exists() else {}
 p=urllib.parse.urlsplit(url); rel=p.path.lstrip('/') or 'index.html'
 if not Path(rel).suffix: rel=rel.rstrip('/')+'/index.html'
 if p.query: rel += '__'+hashlib.sha256(p.query.encode()).hexdigest()[:12]
 dest=ROOT/'public'/rel
 try:
  if dest.exists() and dest.stat().st_size and not dest.with_name(dest.name+'.headers').exists():
   data=dest.read_bytes();ct='application/json' if '/wp-json/' in url else (mimetypes.guess_type(str(dest).split('__')[0])[0] or 'application/octet-stream')
   return {'url':url,'file':str(dest.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'type':ct,'status':200},data,json.loads(dest.with_name(dest.name+'.response.json').read_text()) if dest.with_name(dest.name+'.response.json').exists() else {}
  dest.parent.mkdir(parents=True,exist_ok=True)
  hp=dest.with_name(dest.name+'.headers')
  result=subprocess.run(['curl','-fLsS','--max-time','35','-A','LABG-public-preservation/1.0','-D',str(hp),'-o',str(dest),url],capture_output=True)
  if result.returncode: raise RuntimeError(result.stderr.decode()[:250])
  headers={}
  for line in hp.read_text().splitlines():
   if ': ' in line:
    k,v=line.split(': ',1);headers[k.lower()]=v
  hp.unlink(); data=dest.read_bytes();ct=headers.get('content-type','')
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  return {'url':url,'file':str(dest.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'type':ct,'status':200},data,headers
 except Exception as e:return {'url':url,'status':'failed','error':str(e)},b'',{}
while queue and len(seen)<5000:
 batch=sorted(queue-seen,key=lambda u:(0 if '/wp-json/' in u or u.endswith('.xml') else 1 if any(e in u for e in ['.css','.woff','.js']) else 2 if '/wp-content/' in u or '/wp-includes/' in u else 3,u))[:60];queue.difference_update(batch)
 if not batch:break
 seen.update(batch)
 # Reuse HTTP connections across each batch, instead of a new connection per asset.
 args=['curl','--parallel','--parallel-max','2','--rate','6/m']; pending=[]; batch_errors={}
 for url in batch:
  if url in prior and prior[url].get('status')==200 and (ROOT/prior[url]['file']).exists():continue
  p=urllib.parse.urlsplit(url);rel=p.path.lstrip('/') or 'index.html'
  if not Path(rel).suffix:rel=rel.rstrip('/')+'/index.html'
  if p.query:rel+='__'+hashlib.sha256(p.query.encode()).hexdigest()[:12]
  dest=ROOT/'public'/rel
  if dest.exists() and not dest.with_name(dest.name+'.headers').exists():continue
  dest.parent.mkdir(parents=True,exist_ok=True)
  hp=dest.with_name(dest.name+'.headers')
  args+=['-fLsS','--max-time','40','-A','LABG-public-preservation/1.0','-D',str(hp),'-o',str(dest),url,'--next']
  pending.append((url,dest,hp))
 if pending:
  result=subprocess.run(args[:-1],capture_output=True)
  for url,dest,hp in pending:
   if hp.exists():
    h=hp.read_text();codes=re.findall(r'HTTP/[^ ]+ (\d+)',h)
    if codes and codes[-1]=='200' and dest.exists():
     hd={}
     for line in h.splitlines():
      if ': ' in line:
       k,v=line.split(': ',1)
       if k.lower() in ['content-type','x-wp-totalpages']:hd[k.lower()]=v
     dest.with_name(dest.name+'.response.json').write_text(json.dumps(hd));hp.unlink()
    else: batch_errors[url]='HTTP '+(codes[-1] if codes else 'transfer failed')
 for url in batch:
   if url in batch_errors: rec,data,headers={'url':url,'status':'failed','error':batch_errors[url]},b'',{}
   else: rec,data,headers=get(url)
   records.append(rec)
   if rec['status']!=200:continue
   url=rec['url'];ct=rec['type'];s=data.decode('utf-8',errors='replace') if any(x in ct for x in ['html','css','json','xml','javascript']) else ''
   links=[]
   if 'html' in ct:
    links+=re.findall(r'''(?:href|src|data-src|data-srcset|srcset|poster)\s*=\s*["']([^"']+)''',s)
   if 'xml' in ct:links+=re.findall(r'<loc>(.*?)</loc>',s)
   if 'css' in ct or 'html' in ct:links+=re.findall(r'''url\(\s*["']?([^\)'"\s]+)''',s)
   if 'json' in ct:
    def walk(obj):
     if isinstance(obj,dict):
      for k,v in obj.items():
       if k in ['link','source_url'] and isinstance(v,str) and not (k=='link' and obj.get('type')=='attachment'): links.append(v)
       elif k=='rendered' and isinstance(v,str): links.extend(re.findall(r'''(?:href|src)=["']([^"']+)''',v))
       elif k not in ['media_details','yoast_head','yoast_head_json']: walk(v)
     elif isinstance(obj,list):
      for v in obj: walk(v)
    walk(json.loads(s))
    pages=int(headers.get('X-WP-TotalPages',headers.get('x-wp-totalpages','1')))
    if urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get('page')==['1']:
     for n in range(2,min(pages,100)+1):queue.add(url.replace('&page=1','&page='+str(n)))
    if url.endswith('/types'):
     try:
      for v in json.loads(s).values():
       if v.get('rest_base') and '(' not in v['rest_base'] and v['rest_base'] not in ['font-families','global-styles','menu-items','template-parts','templates']:queue.add(BASE+'wp-json/'+v.get('rest_namespace','wp/v2')+'/'+v['rest_base']+'?per_page=100&page=1')
     except Exception:pass
   for raw in links:
    for link in raw.split(',') if ' ' in raw else [raw]:
     link=html.unescape(link.strip().split(' ')[0]);u=urllib.parse.urljoin(url,link);p=urllib.parse.urlsplit(u)
     if any(c in p.path for c in [chr(92),chr(39),chr(34)]):continue
     if p.netloc not in ['labrewersguild.org','www.labrewersguild.org']:continue
     if any(x in p.path for x in ['/wp-admin','/wp-login','xmlrpc.php','/feed','/wp-json/']):continue
     if p.query and not p.path.startswith('/wp-content/') and not p.path.startswith('/wp-includes/'):continue
     if p.path.endswith(('.mp4','.mov','.zip')):continue
     if '/events/' in p.path and re.search(r'/\d{4}',p.path):continue
     u=urllib.parse.urlunsplit(('https','labrewersguild.org',p.path,p.query,''))
     if u not in seen:queue.add(u)
 (ROOT/'manifest.json').write_text(json.dumps(records,indent=2))
 (ROOT/'pending.json').write_text(json.dumps(sorted((queue-seen)|{r['url'] for r in records if r.get('error')=='HTTP 429'}),indent=2))
 if any(r.get('error')=='HTTP 429' for r in records[-len(batch):]):
  queue.update(r['url'] for r in records[-len(batch):] if r.get('error')=='HTTP 429')
  (ROOT/'pending.json').write_text(json.dumps(sorted(queue-seen|{r['url'] for r in records if r.get('error')=='HTTP 429'}),indent=2))
  print('Rate limited; stopping capture. Resume after the host allows requests.',flush=True)
  break
 print(f'Captured {sum(r["status"]==200 for r in records)}; failures {sum(r["status"]!=200 for r in records)}; pending {len(queue-seen)}',flush=True)
(ROOT/'pending.json').write_text(json.dumps(sorted((queue-seen)|{r['url'] for r in records if r.get('error')=='HTTP 429'}),indent=2))
