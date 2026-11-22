from pathlib import Path
import subprocess,sys
W=Path(__file__).parent
renderer=Path(r'C:/Users/piatkowskigs/.codex/plugins/cache/openai-primary-runtime/documents/26.1117.12345/skills/documents/render_docx.py')
result=subprocess.run([sys.executable,'-X','utf8',str(renderer),str(W/'evaluation-updated.docx'),'--output_dir',str(W/'renderer-attempt-final'),'--emit_pdf'],capture_output=True,text=True,encoding='utf-8')
(W/'renderer-final.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
if result.returncode:
    if 'LibreOffice soffice.exe was not found' not in result.stderr:raise RuntimeError('Unexpected renderer error; inspect log')
    print('Bundled renderer lacks LibreOffice. Using native Word export.',flush=True)
    subprocess.run(['pwsh','-NoProfile','-File',str(W/'render-word.ps1')],check=True)
else:
    raise RuntimeError('Bundled renderer became available; inspect its outputs before changing the QA path')
