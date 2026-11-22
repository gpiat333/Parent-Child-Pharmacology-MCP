from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
W=Path(__file__).parent;version=sys.argv[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
comparison=read(W/'render-comparison.json');changed=sorted(read(W/'slide-map.json')['changed']);pages=len(read(W/'docx-text.json'))
assert comparison['unchanged_slides_identical']==49-len(changed) and not comparison['unintended_differences']
assert pages==10
review={'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
 'docx':{'all_pages_inspected_at_full_size':True,'pages':pages,'renderer':'Native Microsoft Word PDF export, then PyMuPDF page images; bundled renderer attempted but LibreOffice unavailable','layout_findings':[],'sha256':sha(W/'evaluation-updated.docx')},
 'deck':{'changed_slides_inspected_full_size':True,'slides':49,'main_slides':15,'hidden_appendix_slides':34,'changed_slides':changed,'all_slides_reviewed_in_contact_sheets':True,'native_renderer':'Microsoft PowerPoint 1280x720 PNG','unchanged_slide_renders_identical_to_reference':49-len(changed),'unresolved_layout_findings':[],'exact_red_title_disclaimer_visually_confirmed':True,'sha256':sha(W/('output/professional-'+version+'.pptx'))},
 'scope':f'Observed full-size inspection of all {pages} DOCX pages, all {len(changed)} changed slides and title; all 49 slides reviewed in contact sheets. Layout and evidence reporting review, not clinician adjudication.'}
(W/'visual-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
print('Recorded completed visual review.')
