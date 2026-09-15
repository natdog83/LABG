#!/usr/bin/env python3
"""Build inert local preview and editable WordPress page import from captured bytes."""
import os,html,json,re,shutil,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'generated'; OUT.mkdir(exist_ok=True)
records=json.loads((ROOT/'archive/manifest.json').read_text()); ok=[r for r in records if r['status']==200]
assets={r['url']:r for r in ok if not any(x in r['type'] for x in ['text/html','application/json','text/xml','application/xml'])}
asset_paths={u:'/recovered-assets/'+r['file'].removeprefix('public/') for u,r in assets.items()}
variants={}; substitutions={}
for u,r in assets.items():
 if r['type'].startswith('image/'):
  family=re.sub(r'-\d+x\d+(?=\.[^.]+$)','',urllib.parse.urlsplit(u).path)
  if family not in variants or r['bytes']>variants[family][1]:variants[family]=(u,r['bytes'])
def asset_target(url):
 if url in asset_paths:return asset_paths[url]
 path=urllib.parse.urlsplit(url).path;family=re.sub(r'-\d+x\d+(?=\.[^.]+$)','',path)
 if family in variants:
  chosen=variants[family][0];substitutions[url]=chosen;return asset_paths[chosen]
 return None
def rewrite(s,origin):
 s=s.replace(chr(92)+"/","/")
 for u,p in asset_paths.items():
  if not u.startswith('https://labrewersguild.org'):s=s.replace(u,origin+p)
 def replace(m):
  original=html.unescape(m.group(0));parsed=urllib.parse.urlsplit(original)
  normalized=urllib.parse.urlunsplit(('https','labrewersguild.org',parsed.path,parsed.query,''))
  target=asset_target(normalized)
  if target:return origin+target+('#'+parsed.fragment if parsed.fragment else '')
  return origin+parsed.path+('?' + parsed.query if parsed.query else '')+('#'+parsed.fragment if parsed.fragment else '')
 return re.sub(r"https?://(?:www\.)?labrewersguild\.org[^\s\"'<>(),]*",replace,s)

for u,r in assets.items():
 dest=OUT/'assets'/r['file'].removeprefix('public/');dest.parent.mkdir(parents=True,exist_ok=True)
 data=(ROOT/'archive'/r['file']).read_bytes()
 if 'css' in r['type']:
  s=data.decode('utf-8',errors='replace')
  def cssurl(m):
   v=m.group(1).strip('"\' ');absolute=urllib.parse.urljoin(u,v)
   parsed=urllib.parse.urlsplit(absolute)
   fallback=parsed.path if parsed.netloc in ['labrewersguild.org','www.labrewersguild.org'] else v
   return 'url("'+(asset_target(absolute) or fallback)+'")'
  data=re.sub(r'url\(([^)]+)\)',cssurl,s).encode()
 if dest.exists():dest.unlink()
 if 'css' in r['type']: dest.write_bytes(data)
 else: os.link(ROOT/'archive'/r['file'],dest)
pages=[]
sources=[]
for r in ok:
 if 'text/html' not in r['type'] or '/wp-json/' in r['url']:continue
 path=urllib.parse.urlsplit(r['url']).path
 if Path(path).suffix or urllib.parse.urlsplit(r['url']).query:continue
 sources.append((r['url'],(ROOT/'archive'/r['file']).read_text(errors='replace'),'captured_html'))
# Fill missing main pages/articles from public REST content inside the recovered shell.
existing={url for url,_,_ in sources}
home=next((source for url,source,_ in sources if url=='https://labrewersguild.org/'),'')
main=re.search(r"<div id=['\"]main['\"][^>]*>",home)
footer=re.search(r'<footer\b',home)
if main and footer:
 for r in ok:
  if not any('/wp-json/wp/v2/'+t+'?' in r['url'] for t in ['pages','posts']):continue
  for item in json.loads((ROOT/'archive'/r['file']).read_text()):
   url=item.get('link');content=item.get('content',{}).get('rendered','')
   if not url or url in existing:continue
   shell=home[:main.end()]+content+home[footer.start():]
   shell=shell.replace('</head>','<style>#header{position:relative!important;background:#132f40!important}#main{padding-top:0!important}</style></head>')
   shell=re.sub(r'<title[^>]*>.*?</title>','<title>'+item['title']['rendered']+'</title>',shell,flags=re.S)
   sources.append((url,shell,'rest_content_in_reconstructed_shell'));existing.add(url)
for url,s,method in sources:
 path=urllib.parse.urlsplit(url).path
 bm=re.search(r'<body\b([^>]*)>([\s\S]*?)</body>',s,re.I)
 hm=re.search(r'<head[^>]*>([\s\S]*?)</head>',s,re.I)
 if not bm or not hm:continue
 # Preserve styling and rendered content. Strip scripts, embedded frames and live form targets.
 def clean(v):
  v=re.sub(r'<script\b[^>]*>[\s\S]*?</script>','',v,flags=re.I)
  v=re.sub(r'<iframe\b[^>]*>[\s\S]*?</iframe>','<p>[External embed omitted from recovery preview]</p>',v,flags=re.I)
  v=re.sub(r'''\s+on\w+\s*=\s*(?:"[^"]*"|'[^']*')''','',v,flags=re.I)
  v=re.sub(r'''(<form\b[^>]*?)\saction\s*=\s*["'][^"']*["']''',r'\1 action="#"',v,flags=re.I)
  return v
 head=clean(hm.group(1));head=re.sub(r'<(?:title)[^>]*>[\s\S]*?</title>','',head,flags=re.I)
 head=re.sub(r'<(?:link|meta)\b[^>]*(?:canonical|pingback|api.w.org|alternate|og:|twitter:)[^>]*>','',head,flags=re.I)
 head+='''<meta name="robots" content="noindex,nofollow"><style>.avia_transform .avia_animated_image,.avia_transform .av-animated-generic,.avia_transform .avia_start_delayed_animation{opacity:1!important;transform:none!important}.avia-caption-title,.avia-caption-content{opacity:1!important;transform:none!important}.avia-slideshow li:first-child{opacity:1!important;visibility:visible!important}#labg-recovery-note{position:fixed;bottom:0;left:0;right:0;background:#132f40;color:white;padding:8px;text-align:center;z-index:999999;font:13px sans-serif}</style>'''
 body=clean(bm.group(2))+'<div id="labg-recovery-note">Recovered public-site preview — forms, search, maps and membership services are not connected.</div>'
 title=re.search(r'<title[^>]*>(.*?)</title>',s,re.S|re.I)
 attrs=re.search(r'<html\b([^>]*)>',s,re.I)
 page={'url':url,'recovery_method':method,'path':path,'slug':path.strip('/').split('/')[-1] or 'home','title':html.unescape(title.group(1)) if title else path,'head':rewrite(head,'__LABG_ORIGIN__'),'body':rewrite(body,'__LABG_ORIGIN__'),'body_attributes':bm.group(1),'html_attributes':attrs.group(1) if attrs else 'lang="en-US"'}
 pages.append(page)
 dest=OUT/'preview'/path.lstrip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text('<!doctype html><html '+page['html_attributes']+'><head>'+page['head'].replace('__LABG_ORIGIN__','')+'</head><body '+page['body_attributes']+'>'+page['body'].replace('__LABG_ORIGIN__','')+'''<script>document.addEventListener('submit',e=>{e.preventDefault();alert('Preview only: form is not connected.');},true);</script></body></html>''')
(OUT/'image-variant-substitutions.json').write_text(json.dumps(substitutions,indent=2))
(OUT/'pages.json').write_text(json.dumps(pages,indent=2))
# Link assets without duplicating their bytes.
p=OUT/'preview/recovered-assets'
if p.is_symlink():p.unlink()
if not p.exists():p.symlink_to('../assets',target_is_directory=True)
print(json.dumps({'pages':len(pages),'assets':len(assets),'captured':len(ok),'failed':len(records)-len(ok),'bytes':sum(r['bytes'] for r in ok)},indent=2))
