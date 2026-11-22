from pathlib import Path
import hashlib,json,shutil
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
OLD=P/'evaluation/report-context-revision';R=P/'evaluation/grader-attribution-revision'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
origin=json.loads((R/'capture-lineage.json').read_text())
for name,digest in origin['files'].items():assert sha(R/name)==sha(OLD/name)==digest
captures=[R/name for name in origin['files']]
script=(W/'prepare.py').read_text(encoding='utf-8')
exec(compile(script[script.index('bridge='):],str(W/'prepare.py'),'exec'))
