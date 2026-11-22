from pathlib import Path
import json,shutil
R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/grader-attribution-revision')
archive=R/'development/citation-id-candidate';archive.mkdir(parents=True,exist_ok=False)
for name in ['grader_contract.py','grader_runtime.py','score_current.py','tests/test_grader_attribution.py']:
    target=archive/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,target)
for name in ['calibration.json','calibration-summary.json','pilot-verification.json','chat-judgments/E01-gap.json','paired-final/E01-gap-mcp-judge.json']:
    source=(R/name).resolve();target=(archive/name).resolve()
    assert source.is_relative_to(R.resolve()) and target.is_relative_to(archive.resolve())
    target.parent.mkdir(parents=True,exist_ok=True);shutil.move(source,target)
(archive/'STATUS.json').write_text(json.dumps({'final_benchmark':False,'reason':'Citation ID binding removed URL transcription. E01 dose misattribution disappeared, but the model demanded the literal word unranked instead of checking non-ranking behavior. The paired answer also genuinely omitted abstract-availability disclosure. Generic behavior-versus-declaration rubric clarified; all raw findings retained.','fidelity_controls_matched':8,'task_controls_matched':8,'controls':8},indent=2),encoding='utf-8')
print('Preserved citation-ID pilot findings before the final semantic clarification.')
