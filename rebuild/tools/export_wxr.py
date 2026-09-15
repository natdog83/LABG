#!/usr/bin/env python3
"""Reconstruct a WordPress WXR from public REST fields; not an original WP export."""
import json,xml.etree.ElementTree as E
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=R/'generated';out.mkdir(exist_ok=True)
ns={'wp':'http://wordpress.org/export/1.2/','content':'http://purl.org/rss/1.0/modules/content/','dc':'http://purl.org/dc/elements/1.1/','excerpt':'http://wordpress.org/export/1.2/excerpt/'}
for k,v in ns.items():E.register_namespace(k,v)
def tag(parent,name,text):
 if ':' in name:
  a,b=name.split(':',1);name='{'+ns[a]+'}'+b
 E.SubElement(parent,name).text=str(text or '')
rss=E.Element('rss',version='2.0');ch=E.SubElement(rss,'channel')
for k,v in [('title','LA County Brewers Guild — recovered public content'),('link','https://labrewersguild.org'),('description','Reconstructed public REST export; rendered content, no original builder metadata.'),('wp:wxr_version','1.2'),('wp:base_site_url','https://labrewersguild.org'),('wp:base_blog_url','https://labrewersguild.org')]:tag(ch,k,v)
seen=set();counts={}
for rec in json.loads((R/'archive/manifest.json').read_text()):
 if rec['status']!=200 or '/wp-json/wp/v2/' not in rec['url']:continue
 try: data=json.loads((R/'archive'/rec['file']).read_text())
 except Exception:continue
 if not isinstance(data,list):continue
 for p in data:
  if not isinstance(p,dict) or not p.get('id') or not p.get('type') or p['type'] in ['wp_navigation','wp_block']:continue
  key=(p['type'],p['id'])
  if key in seen:continue
  seen.add(key);counts[p['type']]=counts.get(p['type'],0)+1
  item=E.SubElement(ch,'item')
  for k,v in [('title',p.get('title',{}).get('rendered','')),('link',p.get('link')),('dc:creator','labg-recovery'),('content:encoded',p.get('content',{}).get('rendered',p.get('description',{}).get('rendered',''))),('excerpt:encoded',p.get('excerpt',{}).get('rendered','')),('wp:post_id',p['id']),('wp:post_date',p.get('date','').replace('T',' ')),('wp:post_date_gmt',p.get('date_gmt','').replace('T',' ')),('wp:post_name',p.get('slug')),('wp:status','inherit' if p['type']=='attachment' else 'publish'),('wp:post_parent',p.get('parent',0)),('wp:post_type',p['type']),('wp:comment_status','closed'),('wp:ping_status','closed')]:tag(item,k,v)
  if p['type']=='attachment':tag(item,'wp:attachment_url',p.get('source_url'))
  meta=E.SubElement(item,'{'+ns['wp']+'}postmeta');tag(meta,'wp:meta_key','_labg_source_url');tag(meta,'wp:meta_value',p.get('link'))
E.ElementTree(rss).write(out/'public-content-reconstructed.xml',encoding='utf-8',xml_declaration=True)
(out/'structured-counts.json').write_text(json.dumps(counts,indent=2));print(counts)
