from pathlib import Path
import sys
sys.path.insert(0,r'C:/Users/piatkowskigs/Desktop/.submission-evidence-review/pydeps')
from PIL import Image, ImageOps, ImageDraw
import fitz, json, sys
W=Path(r'C:/Users/piatkowskigs/Desktop/.submission-grader-attribution-review')
mode=sys.argv[1]
if mode=='docx':
    src=fitz.open(W/'evaluation-updated.pdf'); out=W/'docx-pages';out.mkdir(exist_ok=True)
    for i,page in enumerate(src,1):page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(out/f'{i}.png')
    files=[out/f'{i}.png' for i in range(1,len(src)+1)]
    (W/'docx-text.json').write_text(json.dumps([p.get_text() for p in src],indent=2),encoding='utf-8')
else:
    out=W/'native-slides';files=sorted(out.glob('*.PNG'),key=lambda p:int(''.join(c for c in p.stem if c.isdigit())))
    if not files:files=sorted(out.glob('*.png'),key=lambda p:int(''.join(c for c in p.stem if c.isdigit())))
cols=2 if mode=='docx' else 3
rows=3 if mode=='docx' else 4
tw,th=(420,565) if mode=='docx' else (426,260)
for start in range(0,len(files),cols*rows):
    canvas=Image.new('RGB',(cols*tw,rows*th),'#dbe4ef');draw=ImageDraw.Draw(canvas)
    for j,path in enumerate(files[start:start+cols*rows]):
        im=Image.open(path).convert('RGB');im.thumbnail((tw-12,th-25))
        x=(j%cols)*tw+(tw-im.width)//2;y=(j//cols)*th+22
        canvas.paste(im,(x,y));draw.text(((j%cols)*tw+8,(j//cols)*th+5),f'{mode} {start+j+1}',fill='black')
    canvas.save(W/f'{mode}-overview-{start//(cols*rows)+1}.png')
print(json.dumps({'mode':mode,'items':len(files),'overviews':(len(files)+cols*rows-1)//(cols*rows)}))

