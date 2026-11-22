from pathlib import Path
import hashlib
import json

W = Path(__file__).parent
P = Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R = P / 'evaluation/grader-attribution-revision'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
summary = read(R / 'summary.json')
freeze = read(R / 'local-source-freeze.json')
for name, expected in freeze['files'].items():
    assert sha(P / name) == expected, name
manifest = read(R / 'evidence-manifest.json')
for name, expected in manifest.items():
    assert sha(R / name) == expected, name
lines = (P / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
package = {line.split('  ', 1)[1]: line.split('  ', 1)[0] for line in lines if line}
assert len(package) == len(lines)
current = [P / 'README.md', P / 'START_HERE.html', P / 'PACKAGING.md',
           P / 'documentation/CURRENT_IMPLEMENTATION.md', P / 'documentation/DATABRICKS_VALIDATION.md',
           P / 'presentation/README.md', P / 'server/README.md', P / 'evaluation/results.json',
           R / 'evidence-manifest.json', R / 'mlflow/parent-final-state.json']
artifacts = read(R / 'final-validation.json')['artifacts']
for name, expected in artifacts.items():
    path = P / name
    assert sha(path) == expected
    current.append(path)
for path in current:
    assert sha(path) == package[path.relative_to(P).as_posix()], str(path)
parent = read(R / 'mlflow/parent-final-state.json')
assert parent['status'] == 'FINISHED'
assert len(parent['submission_artifacts']) == 2
for artifact in parent['submission_artifacts']:
    basename = Path(artifact['path']).name
    match = next(path for path in current if path.name == basename)
    assert artifact['file_size'] == match.stat().st_size, basename
assert summary['local_tests']['tests'] == 562
assert summary['grader_tests']['tests'] == 30
assert summary['calibration']['controls'] == 10
assert not summary['answer_generation_repeated'] and not summary['runtime_source_changed']
assert not summary['deployment_performed_this_revision']
assert not summary['github_push']
out = {'frozen_files_verified': len(freeze['files']),
       'current_evidence_files_verified': len(manifest),
       'package_checksum_entries': len(package),
       'critical_package_files_verified': len(current),
       'mlflow_parent_status': parent['status'],
       'remote_artifact_sizes_match': True,
       'github_push': False}
(W / 'final-integrity-check.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps(out, indent=2))
