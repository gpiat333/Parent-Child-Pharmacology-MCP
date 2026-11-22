from pathlib import Path
import json
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
r01=read(R/'paired-final/R01-mcp.json');record=next(c['result'] for c in r01['calls'] if c['tool']=='get_lactmed_record')
assert record['sections_missing']==[] and record['sections_omitted_by_limit']==[] and record['truncated'] is False
r06=read(R/'paired-final/R06-mcp.json');assert '407-423-7149' not in r06['answer'] and 'clinicaltrials@supernus.com' in r06['answer'] and 'Selected site contacts' in r06['answer']
audit={'manual_score_overrides':False,'clinical_adjudication':False,'findings':[
 {'case':'R01','arm':'mcp','grade_retained':'task fail, fidelity pass','observed':{'sections_found':record['sections_found'],'sections_missing':record['sections_missing'],'sections_omitted_by_limit':record['sections_omitted_by_limit'],'truncated':record['truncated'],'generic_notice':record['section_completeness_notice']},'interpretation':'The grader demands a generic whole-record completeness notice even though all four expected sections were returned without truncation. The answer discloses missing infant-level information. This is a strict disclosure judgment; it is not evidence that the retrieved outcome section was missing or that the answer invented outcomes.'},
 {'case':'R06','arm':'mcp','grade_retained':'task fail, fidelity pass','observed':{'APG_phone_present_in_answer':False,'central_study_contact_present':True,'site_contact_subset_explicitly_labeled':True},'interpretation':'The grader incorrectly says the answer contains the APG main phone but omits its extensions. The answer instead lists central contacts and an explicitly selected subset of site contacts; the APG phone is absent entirely. Whether every site contact is required by the broad contacts criterion is a scope judgment. The score is retained unchanged, and the rationale is flagged for human review.'},
 {'case':'R03','arm':'mcp','grade_retained':'fidelity fail, task pass','interpretation':'The grader flags combining procedural precautions with explicit risk-factor statements in one sentence. The exact sentence appears in the answer; clinical significance and the broader label interpretation have not been independently adjudicated.'}
]}
(R/'technical-grade-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8');print('Saved evidence-based grading caveats without changing scores.')
