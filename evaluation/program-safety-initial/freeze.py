"""Record the exact local source used for this evaluation; verify before reporting."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(p for folder in ['server','chat-client'] for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in {'.py','.ps1','.json','.lock'} and not {'__pycache__','.pytest_cache','.venv'}.intersection(p.parts))
current={p.relative_to(ROOT).as_posix():digest(p) for p in files}
if '--verify' in sys.argv:
 old=json.loads((OUT/'source-freeze.json').read_text())
 assert current==old['files'],'Source changed after the evaluation freeze'
 print('Frozen source verified: '+str(len(current))+' files')
else:
 (OUT/'source-freeze.json').write_text(json.dumps({'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'user_facing_date':'2026-11-21 America/New_York','files':current,'case_file_sha256':digest(OUT/'cases.json'),'unit_tests_sha256':digest(OUT/'unit-tests.xml'),'local_endpoint':'http://127.0.0.1:18080/mcp','model':'system.ai.gpt-5-6-luna','deployment':'none'},indent=2),encoding='utf-8')
 print('Frozen '+str(len(current))+' source files')
