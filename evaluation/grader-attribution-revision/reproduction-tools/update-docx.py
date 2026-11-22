from pathlib import Path
from copy import deepcopy
import json
from docx import Document
from docx.shared import Pt
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/grader-attribution-revision'
S=json.loads((R/'summary.json').read_text(encoding='utf-8-sig'));C=S['chat']['counts'];G=S['chat']['diagnostic_grading'];B=S['paired']
d=Document(W/'reference.docx')
def setp(i,text):
 p=d.paragraphs[i]
 if p.runs:
  p.runs[0].text=text
  for run in p.runs[1:]:run.text=''
 else:p.add_run(text)
setp(2,f'Grader v3 corrects the E01 source-to-answer attribution error. All 42 retained evaluation rows were regraded and verified in MLflow; answers and evidence are unchanged. Research: {G["fidelity_pass"]}/21 fidelity and {G["task_fulfilled"]}/21 tasks. Fresh local tests: 562 server and 30 evaluator tests passed. No app deployment, GitHub upload or official submission occurred in this revision.')
setp(4,'Evidence date: November 21, 2026 Eastern. Policy .9 unchanged; grader v3. Local tests and driver; Databricks model and MLflow.')
d.paragraphs[10].runs[0].text='The deck has 15 main slides and a hidden technical appendix. Saved demos illustrate .4; current grader v3 results replay retained .9 answers.'
setp(18,'Source and evaluator checks')
setp(19,'All 562 server unit tests passed again locally with no failures, errors or skips; application code is unchanged. The separate grader suite has 30 passing tests for attribution, citation binding, cache validity and bounded error correction. All 114 frozen application files match the prior .9 source; 93 runtime files were verified during that prior deployment. The prior inventory of 30 tools, four prompts and four resources is unchanged; those live inventory checks were not repeated.')
setp(21,'The same 28 saved chats, evidence and criteria are retained: seven fixed stops and 21 research answers. Routes, required/allowed tool choices and URL membership were recomputed from the captures. No answer generation or source retrieval was repeated. This isolates the grading change; it is not a new independent sample of model behavior.')
setp(22,'MLflow recording and verification')
setp(23,'MLflow records 21 research, seven stop and 14 paired rows. All applicable scores were read back, including failures; no scorer execution errors remained. Two E01 pilot grades are reused once, not extra samples. Original tool traces remain in artifacts; replay creates one root span per row. Grading uses four workers per sequential phase. No new timing comparison was run.')
setp(25,'Both paired arms retain the same model, prompts and reference pools from .9. Only the grader changed. Only MCP originally had retrieval, workflow enforcement and fixed notices, so this compares workflows rather than isolated model ability. The paired runner omits the companion’s extra source review. The shared bounded pool may contain evidence an answer never received. Candidate and source text are now separated explicitly during grading.')
setp(69,f'Seven paired questions retain 7/7 completed answers per arm. Tasks fulfilled: MCP {B["mcp"]["task_fulfilled"]}/7, plain {B["plain"]["task_fulfilled"]}/7. Fidelity pass/fail/N/A: MCP {B["mcp"]["fidelity_pass"]}/{B["mcp"]["fidelity_fail"]}/{B["mcp"]["fidelity_not_assessable"]}; plain {B["plain"]["fidelity_pass"]}/{B["plain"]["fidelity_fail"]}/{B["plain"]["fidelity_not_assessable"]}. Honest abstention can leave a lookup incomplete. No new answers or latency measurements were generated.')
setp(70,'Grader v3 and limits')
setp(71,'Fidelity asks whether claims are supported by captured evidence. Task fulfillment asks whether every requested requirement was met; a supported answer can still be incomplete. N/A is excluded from fidelity rates. Grader v3 validates negative content quotations against the answer, anchors omissions to requirements and binds citation IDs to exact original URLs. Literal presence and URL membership do not prove relevance, clinical accuracy or safety.')
fail_label='failure' if G['fidelity_fail']==1 else 'failures'
setp(72,f'Research grades: {G["fidelity_pass"]} fidelity passes, {G["fidelity_fail"]} {fail_label}; {G["task_fulfilled"]}/21 tasks fulfilled. Ten synthetic development controls match both dimensions. Earlier grader candidates and all raw attempts are preserved. The first structurally valid grade is retained, including failures; retries address invalid attribution or schema only. E01 main now passes. Its paired answer omits the required missing-abstract disclosure, so its task failure remains. Known cases, one retained answer each, bounded references and a same-family judge limit interpretation. No score overrides or clinician review occurred.')
d.paragraphs[72].paragraph_format.space_before=Pt(6)
setp(78,'Historical evidence and source lineage')
setp(79,'On these same .9 answers, historical grader v2 reported research fidelity 21/21 and tasks 20/21, with paired tasks MCP 6/7 and plain 1/7. It wrongly attributed reference doses to E01 answers. New v3 scores reflect grading changes, not changed answers. Older .5 results (531 tests, research tasks 18/21, paired MCP 5/7 and plain 0/7) used different code. Other intermediate runs and raw grades remain archived. Demos illustrate .4. Current source and retained captures are identified by frozen hashes.')
setp(80,'Databricks delivery and traceability')
setp(81,'The existing mcp-mc Databricks sandbox app remains on policy .9 and the same deployment ID. Only evaluation code and submission documents changed in this revision. The driver and both unit suites ran locally; grading and MLflow used existing Databricks services. No infrastructure, permissions, app deployment or GitHub upload occurred. Raw captures, grades, provenance and readbacks are in evaluation/grader-attribution-revision. This is not production readiness or clinical certification.')
t=next(t for t in d.tables if t.cell(0,0).text=='Current measure')
# Preserve native table formatting while adding a distinct evaluator-test row.
t.rows[1]._tr.addnext(deepcopy(t.rows[1]._tr))
values=[('Server unit tests','562 passed','Fresh local rerun; application unchanged'),('Evaluator unit tests','30 passed','Separate grader regression suite'),('Retained chats',f'{C["completed"]["passed"]}/28','Rechecked; no new answers'),('Expected routes',f'{C["boundary_behavior"]["passed"]}/28','Retained trace checks'),('Tool checks',f'{C["tool_selection"]["passed"]}/28','Required/allowed selections'),('Fixed stops',f'{C["fixed_stops"]["passed"]}/7','Zero downstream calls in retained traces'),('URL membership',f'{C["citation_provenance"]["passed"]}/21','Membership is not claim support'),('Research grades',f'{G["fidelity_pass"]} fidelity passes; {G["task_fulfilled"]}/21 tasks','Separate fallible model judgments')]
assert len(t.rows)-1==len(values)
for row,vals in zip(t.rows[1:],values):
 for cell,value in zip(row.cells,vals):
  p=cell.paragraphs[0]
  if p.runs:
   p.runs[0].text=value
   for run in p.runs[1:]:run.text=''
  else:p.add_run(value)
for rel in d.part.rels.values():
 if rel.is_external and 'evaluation/report-context-revision/' in rel.target_ref:rel._target=rel.target_ref.replace('evaluation/report-context-revision/','evaluation/grader-attribution-revision/')
d.save(W/'evaluation-updated.docx')
print('Updated the existing evaluation DOCX.')
