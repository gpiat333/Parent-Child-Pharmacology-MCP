from pathlib import Path
W=Path(__file__).parent;OLD=W.with_name('.submission-grader-attribution-review')
for name in ['check-artifact-metrics.py','record-visual-review.py','refresh-final-manifests.py','check-package-links.py']:
 s=(OLD/name).read_text(encoding='utf-8').replace('evaluation/grader-attribution-revision','evaluation/abstract-disclosure-revision').replace('grader-attribution-revision/REPORT.md','abstract-disclosure-revision/REPORT.md').replace('562 passed','592 passed').replace("cell(44, 4, col), '0'","cell(44, 4, col), '7'").replace('Retained summary.json','Fresh-run summary.json')
 (W/name).write_text(s,encoding='utf-8')
p=W/'compare-rendered-slides.py';s=p.read_text(encoding='utf-8').replace('.submission-report-context-review/native-slides','.submission-grader-attribution-review/native-slides').replace(".read_text())",".read_text(encoding='utf-8'))");p.write_text(s,encoding='utf-8')
print('Prepared consistency and final integrity helpers.')
