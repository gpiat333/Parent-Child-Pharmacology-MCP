from pathlib import Path
import os
W=Path(__file__).parent;OLD=W.parent/'.submission-report-context-review'
for name in ['finalize.mjs','render-deck.ps1','render-docx-with-fallback.py','render-word.ps1','qa-images.py','promote.py','check-package-links.py','compare-rendered-slides.py']:
    text=(OLD/name).read_text(encoding='utf-8')
    text=text.replace('.submission-report-context-review','.submission-grader-attribution-review').replace('evaluation/report-context-revision','evaluation/grader-attribution-revision').replace("P/'evaluation/report-context-revision'","P/'evaluation/grader-attribution-revision'").replace('before-final-report-context-evaluation','before-grader-v3-evaluation')
    (W/name).write_text(text,encoding='utf-8')
print('Prepared artifact rendering and promotion helpers.')
