from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/grader-attribution-revision';version=sys.argv[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (W/'visual-review.json').exists(),'Record the observed visual review before promoting.'
pairs=[(W/('output/professional-'+version+'.pptx'),P/'presentation/Parent-child Pharmacology MCP — Updated.pptx',W/'reference.pptx',P/'presentation/archive/before-grader-v3-evaluation.pptx'),(W/'evaluation-updated.docx',P/'documentation/Parent-child Pharmacology MCP - Evaluation.docx',W/'reference.docx',P/'documentation/archive/before-grader-v3-evaluation.docx')]
for src,target,ref,archive in pairs:
    assert target.is_relative_to(P) and archive.is_relative_to(P)
    assert sha(target)==sha(ref),'Canonical artifact changed since inspection'
    archive.parent.mkdir(parents=True,exist_ok=True)
    if archive.exists():assert sha(archive)==sha(ref)
    else:shutil.copy2(target,archive)
    shutil.copy2(src,target);assert sha(src)==sha(target)
shutil.copy2(W/('deck-validation-'+version+'.json'),R/'presentation-validation.json')
shutil.copy2(W/'visual-review.json',R/'artifact-review.json')
print('Promoted reviewed deck and DOCX; prior local versions archived.')
