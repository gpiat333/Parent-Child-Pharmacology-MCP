from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
from docx import Document
W=Path(__file__).parent
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
slides={}
with zipfile.ZipFile(W/'reference.pptx') as z:
    for n in [13,14,15,42,43,44,45,46,47]:
        root=ET.fromstring(z.read(f'ppt/slides/slide{n}.xml'))
        slides[n]=[{ 'name':s.find('.//p:cNvPr',ns).get('name'),'text':'\n'.join(x.text or '' for x in s.findall('.//a:t',ns))} for s in root.findall('.//p:sp',ns)]
(W/'reference-text.json').write_text(json.dumps({'slides':slides,'paragraphs':[{'i':i,'text':p.text} for i,p in enumerate(Document(W/'reference.docx').paragraphs)]},indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(slides[13],indent=2))
