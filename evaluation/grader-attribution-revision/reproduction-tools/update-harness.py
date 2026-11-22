from pathlib import Path
import shutil,zipfile,json
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/grader-attribution-revision')
helpers=R/'reproduction-tools';assert helpers.exists()
for pattern in ['*.py','*.mjs','*.ps1']:
 for path in sorted(W.glob(pattern)):shutil.copy2(path,helpers/path.name)
design=json.loads((R/'run-design-verification.json').read_text(encoding='utf-8-sig'))
with zipfile.ZipFile(R/'evaluation-harness.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(helpers.iterdir()):
  if f.is_file():z.write(f,f.relative_to(R).as_posix())
 for name in design['evaluator_files']:z.write(R/name,name)
print('Refreshed helper archive; final manifest refresh will hash it before delivery.')
