from pathlib import Path
W=Path(__file__).parent;OLD=W.with_name('.submission-grader-attribution-review')
for name in ['finalize.mjs','render-deck.ps1','render-docx-with-fallback.py','render-word.ps1','qa-images.py','promote.py','compare-rendered-slides.py']:
 s=(OLD/name).read_text(encoding='utf-8').replace('.submission-grader-attribution-review','.submission-abstract-disclosure-review').replace('evaluation/grader-attribution-revision','evaluation/abstract-disclosure-revision').replace('before-grader-v3-evaluation','before-abstract-disclosure-evaluation')
 (W/name).write_text(s,encoding='utf-8')
print('Prepared native render and review helpers.')
