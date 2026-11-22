from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from datetime import datetime,timezone
import json,zipfile,xml.etree.ElementTree as ET
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');D=P/'presentation/current-demo';R=P/'evaluation/grader-attribution-revision'
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='article':self.ids.append(a.get('id'))
def check(base,url):
    u=urlsplit(url)
    if u.scheme in {'http','https'}:assert u.netloc,url;return 'external'
    assert not u.scheme,url
    if not u.path:return 'anchor'
    target=(base/unquote(u.path)).resolve();assert target.is_relative_to(P.resolve()),target
    assert target.exists(),target
    return 'local'
checks=[]
for path in [P/'START_HERE.html',D/'index.html',R/'index.html']:
    parser=Links();parser.feed(path.read_text(encoding='utf-8'));counts={'local':0,'external':0,'anchor':0}
    for href in parser.links:counts[check(path.parent,href)]+=1
    checks.append({'file':path.relative_to(P).as_posix(),'links':counts,'articles':parser.ids})
cards=json.loads((D/'cards.json').read_text());assert checks[1]['articles']==[c['id'] for c in cards] and len(cards)==8
for card in cards:assert (D/(card['id']+'.png')).exists() and (P/'evaluation/notice-citation-revision'/card['source']).exists()
with zipfile.ZipFile(P/'documentation/Parent-child Pharmacology MCP - Evaluation.docx') as z:
    root=ET.fromstring(z.read('word/_rels/document.xml.rels'));doclinks=[n.get('Target') for n in root if n.get('Type','').endswith('/hyperlink')]
    for href in doclinks:check(P/'documentation',href)
out={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'docx_hyperlinks':len(doclinks),'cards':8,'missing_local_links':0,'external_url_structure_only':True,'demo_is_predeployment_local_replay':True}
(R/'package-links.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
