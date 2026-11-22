"""Compare the user's .5 baseline with the final frozen source; no edits."""
from pathlib import Path
from datetime import datetime, timezone
import difflib, hashlib, json

W = Path(__file__).parent
P = Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R = P / 'evaluation/report-context-revision'
B = P / 'evaluation/brief-paraphrase-revision'
read = lambda path: json.loads(path.read_text(encoding='utf-8-sig'))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
before = read(B / 'local-source-freeze.json')['files']
after = read(R / 'local-source-freeze.json')['files']
changed = []
patch = []
for name in sorted(before.keys() | after.keys()):
    old, new = B / 'source-snapshot' / name, P / name
    if name in before:
        assert sha(old) == before[name], name
    if name in after:
        assert sha(new) == after[name], name
    if before.get(name) == after.get(name):
        continue
    changed.append({'file': name, 'before_sha256': before.get(name), 'after_sha256': after.get(name)})
    old_lines = old.read_text(encoding='utf-8-sig').splitlines(keepends=True) if name in before else []
    new_lines = new.read_text(encoding='utf-8-sig').splitlines(keepends=True) if name in after else []
    patch.extend(difflib.unified_diff(old_lines, new_lines, fromfile='baseline-.5/' + name, tofile='final-.9/' + name))
(R / 'cumulative-source-changes.diff').write_text(''.join(patch), encoding='utf-8')
out = {'created_at_utc': datetime.now(timezone.utc).isoformat(),
       'baseline_policy': '2026-11-21.5', 'final_policy': '2026-11-21.9',
       'baseline_frozen_files': len(before), 'final_frozen_files': len(after),
       'files_changed': len(changed), 'changes': changed,
       'scope': 'All frozen runtime/client/test changes across this repair cycle. Documentation is reviewed separately.'}
(R / 'cumulative-source-changes.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps({'files_changed': len(changed), 'final_frozen_files': len(after)}))
