from pathlib import Path
import json
from docx import Document
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/notice-citation-revision'
S=json.loads((R/'summary.json').read_text(encoding='utf-8'));C=S['chat']['counts'];G=S['chat']['diagnostic_grading'];B=S['paired']
d=Document(W/'reference.docx')
def setp(i,text):
 p=d.paragraphs[i]
 if p.runs:
  p.runs[0].text=text
  for run in p.runs[1:]:run.text=''
 else:p.add_run(text)
setp(2,f'The local prototype passes 508 unit tests. The rerun completed {C["completed"]["passed"]}/28 chats with {C["tool_selection"]["passed"]}/28 required/allowed tool checks. Seven paired questions produced 14 answers. This revision preserves required caveats in final answers and fixes adjacent-link parsing. Nothing was deployed or pushed.')
setp(19,'508 unit tests passed with zero failures, errors or skips. The freeze contains 112 server and companion files. The local MCP exposes 30 tools, four prompts and four resources. Twenty direct source/contract and workflow probes were retained. The 35 added regressions cover required notices, stop priority, Python/PowerShell parity, repeated rendering and URL boundaries, including the actual prior R12 answer.')
setp(21,'The same 28 questions from the preceding 473-test run are retained. Seven intended stops are assessed as fixed contracts. The other 21 cases receive diagnostic model grades against retrieved evidence. Required/allowed-tool checks and source-URL membership are separate from clinical interpretation. Only URL extraction changed in the execution checker; allowed tools and task criteria are unchanged.')
setp(22,'Required caveats and citation-checker correction')
setp(23,'The prior run omitted the activity-code interpretation caveat in P01 and the human clinical-review statement in S6-pregnancy. The client now appends applicable fixed notices from trusted local policy after generation. Before-notice text and notice IDs are retained. R12 failed because the URL regex joined adjacent citations. Corrected extraction passes on that same saved answer; the original 20/21 score remains historical.')
setp(25,'Both arms use the same model and unchanged shared instructions. Only MCP receives retrieval tools, enforces preflight workflows and appends applicable fixed notices. Plain has no tools or appended notices. A shared bounded reference pool is judged without arm labels. This compares workflows, not raw-model ability. The paired runner omits the companion\'s longer prompt and separate source-review stage.')
setp(61,'Whole-question safety, identity, privacy and language checks precede research. Explicit brief requests still require medication_evidence_brief first. Final clinical-evidence answers receive a fixed human-review notice; funding answers receive the activity-code caveat. These are application contracts, not source quotations. Stop responses receive no extra research notices. Language thresholds are unchanged and can overblock short technical English. Every third-party client must enforce the contracts.')
setp(69,f'Seven paired questions produced MCP 7/7 and plain 7/7 completed answers. Diagnostic task labels were MCP {B["mcp"]["task_fulfilled"]}/7 and plain {B["plain"]["task_fulfilled"]}/7. Only MCP has retrieval, workflow enforcement and fixed notices. Honest inability can leave a lookup incomplete without being false. Median successful-attempt times were {B["mcp"]["median_seconds"]} and {B["plain"]["median_seconds"]} seconds under parallel load; incomplete attempts and retry delays are excluded.')
setp(71,f'The questions, criteria and grader v2 prompt match the prior 473-test run. Four synthetic controls matched {S["chat"]["calibration"]["fidelity_matches"]}/4 fidelity and {S["chat"]["calibration"]["task_matches"]}/4 task expectations. They do not validate clinical grading. Known cases, single samples, changing sources, same-family judging and bounded references limit comparison. No clinician adjudication occurred. A required caveat cannot by itself prevent false reassurance or harmful framing.')
setp(72,f'P01 and S6-pregnancy now contain their missed notices; all {S["required_notice_records"]} applicable records preserve the text. Raw grades retain {G["fidelity_fail"]} fidelity failure and {21-G["task_fulfilled"]} unmet tasks. The D05 grader appears to confuse participant counts with doses; the P01 grader flags a missing fiscal-year group and mislabels its application notice as a source claim. E01 needs signal/population review. grading-review.json separates observations from unchanged raw scores. No clinician adjudication occurred.')
setp(79,'The prior 473-test run remains under evaluation/brief-routing-revision, including its 19/21 task result, two omitted caveats and raw 20/21 URL score. Its matching source snapshot is preserved. The 445, 443, 395, 359 and 301-test runs and earlier remote checks are historical. They do not validate the current source. Existing managed model access was used without credential renewal or provider changes.')
t=next(t for t in d.tables if t.cell(0,0).text=='Current measure')
values=[('Unit tests','508 passed','Zero failures, errors or skips'),('Chat completion',f'{C["completed"]["passed"]}/28','Current final cases; prior runs retained'),('Expected routes',f'{C["boundary_behavior"]["passed"]}/28','Same known evaluation cases'),('Tool checks',f'{C["tool_selection"]["passed"]}/28','Required/allowed selections'),('Fixed stops',f'{C["fixed_stops"]["passed"]}/7','Zero downstream evidence/model calls'),('URL provenance',f'{C["citation_provenance"]["passed"]}/21','Corrected parser; membership only'),('Research grades',f'{G["fidelity_pass"]} fidelity passes; {G["task_fulfilled"]}/21 tasks','Fallible diagnostic model labels')]
for row,vals in zip(t.rows[1:],values):
 for c,value in zip(row.cells,vals):
  p=c.paragraphs[0]
  if p.runs:
   p.runs[0].text=value
   for run in p.runs[1:]:run.text=''
  else:p.add_run(value)
for rel in d.part.rels.values():
 if rel.is_external and 'evaluation/brief-routing-revision/' in rel.target_ref:rel._target=rel.target_ref.replace('evaluation/brief-routing-revision/','evaluation/notice-citation-revision/')
d.save(W/'evaluation-updated.docx')
print('Updated the existing evaluation DOCX.')
