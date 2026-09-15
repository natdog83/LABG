#!/usr/bin/env python3
"""Validate archive integrity, import counts and local preview dependencies."""
import re,hashlib,html,json,urllib.parse,xml.etree.ElementTree as E
from html.parser import HTMLParser
from pathlib import Path
R=Path(__file__).resolve().parents[1]; records=json.loads((R/'archive/manifest.json').read_text())
errors=[]
for r in records:
 if r['status']!=200:continue
 p=R/'archive'/r['file']
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:errors.append('Archive mismatch: '+r['url'])
pages=json.loads((R/'generated/pages.json').read_text());E.parse(R/'generated/public-content-reconstructed.xml')
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.assets=[];self.scripts=[];self.forms=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'srcset' in d:
   self.assets.extend(x.strip().split(' ')[0] for x in d['srcset'].split(','))
  if tag=='script':self.scripts.append(d)
  if tag=='form':self.forms.append(d.get('action',''))
  if tag in ['img','source','video','audio']:self.assets.append(d.get('src',''))
  if tag=='link' and d.get('rel')=='stylesheet':self.assets.append(d.get('href',''))
missing=[];external=[]
for page in pages:
 p=R/'generated/preview'/page['path'].lstrip('/')/'index.html';s=p.read_text();h=Parser();h.feed(s)
 h.assets.extend(re.findall(r'''url\(\s*["']?([^\)'"\s]+)''',s))
 if '__LABG_ORIGIN__' in s:errors.append('Unresolved origin: '+page['path'])
 if len(h.scripts)!=1:errors.append('Unexpected preview script count: '+page['path'])
 if any(x not in ['', '#'] for x in h.forms):errors.append('Live form target: '+page['path'])
 for url in h.assets:
  if not url or url.startswith('data:'):continue
  if url.startswith(('https:','http:','//')):external.append({'page':page['path'],'asset':url});continue
  rel=urllib.parse.unquote(urllib.parse.urlsplit(html.unescape(url)).path).lstrip('/')
  if rel and not (R/'generated/preview'/rel).exists():missing.append({'page':page['path'],'asset':url})
css_missing=[]
for css in (R/'generated/assets').rglob('*'):
 if not css.is_file() or '.css' not in css.name:continue
 for url in re.findall(r'''url\(\s*["']?([^\)'"\s]+)''',css.read_text(errors='replace')):
  if url.startswith(('data:','http:','https:','//','#')):continue
  rel=urllib.parse.unquote(urllib.parse.urlsplit(url).path)
  dest=R/'generated/preview'/rel.lstrip('/') if rel.startswith('/') else css.parent/rel
  if not dest.exists():css_missing.append({'css':str(css.relative_to(R)), 'asset':url})
result={'missing_css_asset_references':css_missing,'integrity_errors':errors,'preview_pages':len(pages),'missing_asset_references':missing,'external_asset_references':external,'source_fetch_failures':[x for x in records if x['status']!=200],'pending_urls':len(json.loads((R/'archive/pending.json').read_text())),'php_docker_runtime_tested':False,'local_browser_visual_tested':False}
(R/'generated/verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v if not isinstance(v,list) else len(v) for k,v in result.items()},indent=2))
if errors:raise SystemExit(1)
