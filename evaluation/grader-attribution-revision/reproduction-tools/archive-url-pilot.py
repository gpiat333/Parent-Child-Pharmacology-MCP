from pathlib import Path
import json,shutil
R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/grader-attribution-revision')
archive=R/'development/url-copy-candidate';archive.mkdir(parents=True,exist_ok=False)
for name in ['grader_contract.py','grader_runtime.py','tests/test_grader_attribution.py']:
    target=archive/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,target)
initial=R/'development/initial-v3-candidate'
text=(R/'grader_contract.py').read_text(encoding='utf-8')
for addition in ['Epistemic limits such as not evidence of safety or does not establish safety are\ncautions about what missing/limited evidence can prove, not positive medical\nclaims requiring another reference. Specific assertions of safety, harm or risk\nstill require source support.\n',
                 'Task completion requires correctly supplying the requested result, not merely\nmentioning its topic. Reversing an explicitly requested study direction fails that\nrequirement as well as source fidelity. The dimensions are still separate: an\nunsupported ancillary statement need not make an otherwise fulfilled task fail.\n']:
    assert addition in text;text=text.replace(addition,'')
(initial/'grader_contract.py').write_text(text,encoding='utf-8');shutil.copy2(R/'grader_runtime.py',initial/'grader_runtime.py')
for name in ['calibration.json','calibration-summary.json','chat-judgments/E01-gap.json','paired-final/E01-gap-mcp-judge.json']:
    source=(R/name).resolve();target=(archive/name).resolve()
    assert source.is_relative_to(R.resolve()) and target.is_relative_to(archive.resolve())
    target.parent.mkdir(parents=True,exist_ok=True);shutil.move(source,target)
(archive/'STATUS.json').write_text(json.dumps({'final_benchmark':False,'reason':'All eight rubric controls matched, but the E01 paired grader mistyped one long candidate URL on all three attempts. No paired score was accepted. Candidate citation IDs will bind exact original URLs without model transcription.','fidelity_controls_matched':8,'task_controls_matched':8,'controls':8,'E01_paired_score_assigned':False},indent=2),encoding='utf-8')
print('Preserved the unsuccessful URL-transcription attempts and candidate grader source.')
