from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
W=Path(__file__).parent
R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/report-context-revision')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
capture=R/'paired-final/E01-gap-mcp.json';grade=R/'paired-final/E01-gap-mcp-judge.json';reference=R/'paired-final/E01-gap-reference.json'
d=read(capture);g=read(grade)['judgment'];answer=d['answer'];pool=json.dumps(read(reference)+d['calls'],ensure_ascii=False)
checks={'quoted_8_and_10_times_in_answer':'8 and 10 times' in answer,
        'quoted_8_and_10_times_in_reference':'8 and 10 times' in pool,
        'numeric_50_mg_in_answer':bool(re.search(r'50\s*mg\b',answer,re.I)),
        'numeric_50_mg_in_reference':bool(re.search(r'50\s*mg\b',pool,re.I)),
        'numeric_mg_per_kg_per_day_in_answer':bool(re.search(r'\d\s*mg/kg/day',answer,re.I)),
        'grader_quotes_50_mg':'50 mg' in g['rationale'],
        'separate_faers_context_in_answer':'FDA FAERS report-only context' in answer}
assert checks['quoted_8_and_10_times_in_reference'] and checks['numeric_50_mg_in_reference'] and checks['grader_quotes_50_mg']
assert not checks['quoted_8_and_10_times_in_answer'] and not checks['numeric_50_mg_in_answer'] and not checks['numeric_mg_per_kg_per_day_in_answer']
assert not g['task_fulfilled']
out={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'case':'E01-gap','arm':'mcp','checks':checks,'raw_task_fulfilled':False,'raw_score_changed':False,'capture_sha256':sha(capture),'grade_sha256':sha(grade),'reference_sha256':sha(reference),'scope':'Exact disputed text only; not an exhaustive clinical review or adjusted pass rate. The empty exposure row lacks a direct citation, which remains a presentation limitation.'}
chat_input=R/'chat-judge-inputs/E01-gap.json';chat_grade=R/'chat-judgments/E01-gap.json'
ci=read(chat_input);cg=read(chat_grade)['judgment'];ca=ci['answer'];cr=json.dumps(ci['reference_evidence'],ensure_ascii=False)
chat_checks={'quoted_8_and_10_times_in_answer':'8 and 10 times' in ca,
             'quoted_8_and_10_times_in_reference':'8 and 10 times' in cr,
             'numeric_50_mg_in_answer':bool(re.search(r'50\s*mg\b',ca,re.I)),
             'numeric_50_mg_in_reference':bool(re.search(r'50\s*mg\b',cr,re.I)),
             'half_lives_in_answer':bool(re.search(r'half[- ]lives',ca,re.I)),
             'half_lives_in_reference':bool(re.search(r'half[- ]lives',cr,re.I))}
assert not chat_checks['quoted_8_and_10_times_in_answer'] and not chat_checks['numeric_50_mg_in_answer'] and not chat_checks['half_lives_in_answer']
assert chat_checks['quoted_8_and_10_times_in_reference'] and chat_checks['numeric_50_mg_in_reference'] and chat_checks['half_lives_in_reference'] and not cg['task_fulfilled']
out['chat_E01_audit']={'checks':chat_checks,'raw_task_fulfilled':False,'input_sha256':sha(chat_input),'grade_sha256':sha(chat_grade),'raw_score_changed':False}
(R/'grader-attribution-audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
notes=read(W/'technical-notes.json')
notes['mcp:E01-gap']='The answer now displays FAERS report terms and counts separately from the empty clinical-outcome row, retaining population uncertainty and noncausation/denominator caveats. The grader quotes an 8-and-10-times exposure statement, 50 mg and mg/kg/day values as answer text; those numeric regimens are absent from the answer and present in the reference. The exact-text audit documents that misattribution without changing the task failure. The empty exposure row does lack a direct citation, a separate presentation limitation. No clinician adjudication or adjusted pass rate is claimed.'
notes['chat:E01-gap']='The final chat displays separate FAERS report terms and counts with uncertainty and keeps the clinical-outcome row empty. The grader attributes an 8-and-10-times statement, 50 mg and half-life eligibility timing to the answer; none is present in the final answer, while all occur in the supplied reference. The exact-text audit documents the misattribution. The uncited LactMed applicability sentence remains a presentation limitation; no score override or clinical pass is assigned.'
(W/'technical-notes.json').write_text(json.dumps(notes,indent=2,ensure_ascii=False),encoding='utf-8')
(W/'grading-note.txt').write_text('E01 task flags quote reference doses absent from the answers. Raw grades retained; no clinician review.',encoding='utf-8')
print(json.dumps(out,indent=2))
