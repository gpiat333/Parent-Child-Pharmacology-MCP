from pathlib import Path
import json,shutil
R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/grader-attribution-revision')
archive=R/'development/initial-v3-candidate';archive.mkdir(parents=True,exist_ok=False)
files=['calibration.json','calibration-summary.json','pilot-verification.json','chat-judgments/E01-gap.json','paired-final/E01-gap-mcp-judge.json']
for name in files:
    source=(R/name).resolve();target=(archive/name).resolve()
    assert source.is_relative_to(R.resolve()) and target.is_relative_to(archive.resolve())
    target.parent.mkdir(parents=True,exist_ok=True);shutil.move(source,target)
(archive/'STATUS.json').write_text(json.dumps({'final_benchmark':False,'reason':'Pre-freeze synthetic controls exposed an epistemic-caveat false flag and a reversed-result task false pass. Raw grades retained. Generic rubric definitions clarified before the final run.','fidelity_controls_matched':7,'task_controls_matched':7,'controls':8},indent=2),encoding='utf-8')
print('Archived initial candidate grades without altering their scores.')
