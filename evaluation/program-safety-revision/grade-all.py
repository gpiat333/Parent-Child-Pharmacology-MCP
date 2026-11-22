from pathlib import Path
import json,time,subprocess,sys
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/program-safety-revision')
for _ in range(120):
 cases=json.loads((R/'cases.json').read_text());done=[json.loads((R/'chats'/(c['id']+'-results.json')).read_text(encoding='utf-8-sig')).get('completed',False) for c in cases]
 if all(done):break
 time.sleep(10)
else:raise RuntimeError('Incomplete chat cases; inspect retained infrastructure attempts')
for phase in ['chat-judge','paired-judge']:
 result=subprocess.run([sys.executable,str(W/'retry-evaluation.py'),phase])
 if result.returncode:raise RuntimeError('Grading failed: '+phase)
