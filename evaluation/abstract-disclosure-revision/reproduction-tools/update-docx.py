from pathlib import Path
import json
from docx import Document
from docx.shared import Pt
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision'
S=json.loads((R/'summary.json').read_text(encoding='utf-8'));C=S['chat']['counts'];G=S['chat']['diagnostic_grading'];B=S['paired'];d=Document(W/'reference.docx')
def setp(i,text):
 p=d.paragraphs[i]
 if p.runs:
  p.runs[0].text=text
  for run in p.runs[1:]:run.text=''
 else:p.add_run(text)
setp(2,f'Local MCP .10 makes missing abstracts explicit and improves source-grounded summaries. Fresh evaluations: research {G["fidelity_pass"]}/21 fidelity and {G["task_fulfilled"]}/21 tasks; paired MCP {B["mcp"]["task_fulfilled"]}/7 and plain {B["plain"]["task_fulfilled"]}/7 tasks. All 42 rows were verified in MLflow. Tests: 592 server and 30 grader pass. No app deployment, GitHub upload or official submission occurred.')
setp(4,'Evidence date: November 21, 2026 Eastern. Local MCP .10; deployed .9 unchanged. Grader v3 and cases unchanged.')
d.paragraphs[10].runs[0].text='The deck has 15 main slides and a hidden technical appendix. Saved demos illustrate .4; current .10 results use fresh local answers and retrieval.'
setp(18,'Source, contract and protocol checks')
setp(19,f'All 592 server tests and 30 separate grader tests passed locally without failures, errors or skips. Thirty new tests cover abstract gaps, failed retrieval, combination products and Python/PowerShell disclosure parity. {S["source_files"]} application files are frozen. Official MCP Inspector CLI passed {S["inspector"]["passed"]}/{S["inspector"]["checks"]} local checks, including 30 tool schemas, four prompts, four resources, stops, abstract disclosure and a rejected negative result limit.')
setp(21,'All 28 chats were generated afresh against local MCP .10: 21 research answers and seven fixed stops. Live retrieval was repeated. Coverage identifies requested PMIDs with abstract text, missing text, unreturned records or failed requests. The composite preserves this field, and both companion clients append a mandatory disclosure. General instructions also preserve recall candidates, study comparators and unspecified specimens, and discourage unsupported additions.')
setp(22,'MLflow recording and verification')
setp(23,'The final MLflow runs contain 21 research, seven stop and 14 paired rows, all read back with no scorer errors. An initial paired attempt had only 13 scored table rows for 14 traces; all 14 were re-logged from unchanged grades, without new answers or judge calls. The initial attempt is archived and excluded from the final count. Drivers run locally; models and tracking use Databricks. Full tool traces remain in artifacts. These are not remote notebook unit tests.')
setp(25,'Both paired arms use the same model and shared updated instructions, with fresh answers and tool-retrieved reference pools. Normal source caches and dated snapshots still apply. Only MCP receives tools, enforced routing and notices. The paired runner omits the companion’s extra source review. This compares workflows rather than isolated model ability. The bounded shared pool may contain material an answer never received. Cases and grader v3 core are unchanged.')
setp(69,f'Seven fresh paired questions produced 7/7 completed answers per arm. Tasks fulfilled: MCP {B["mcp"]["task_fulfilled"]}/7, plain {B["plain"]["task_fulfilled"]}/7. Fidelity pass/fail/N/A: MCP {B["mcp"]["fidelity_pass"]}/{B["mcp"]["fidelity_fail"]}/{B["mcp"]["fidelity_not_assessable"]}; plain {B["plain"]["fidelity_pass"]}/{B["plain"]["fidelity_fail"]}/{B["plain"]["fidelity_not_assessable"]}. Honest abstention can leave a lookup incomplete. No clinical accuracy or speed claim is made.')
setp(70,'Separate grades and their limitations')
setp(71,'Fidelity asks whether claims are supported by captured evidence. Task fulfillment asks whether requested requirements were met; a supported answer can still be incomplete. N/A is excluded from fidelity rates. Grader v3 validates negative answer quotations, anchors omissions to requirements and binds citation IDs to original URLs. Literal presence and URL membership do not establish relevance, medical truth or safety. Other MCP clients must honor the display contract themselves.')
e=next(r for r in S['grading_rows'] if r['case']=='E01-gap' and r['arm']=='mcp')
remaining=[f'{r["case"]}/{r["arm"]}' for r in S['remaining_negative_grades'] if r['arm']!='plain']
note='Remaining MCP negative grades: '+', '.join(remaining)+'.' if remaining else 'No MCP negative grades were assigned in this sample.'
setp(72,f'Research: {G["fidelity_pass"]} fidelity passes; {G["task_fulfilled"]}/21 tasks. Paired E01: fidelity {e["fidelity"]}, task {"fulfilled" if e["task_fulfilled"] else "not fulfilled"}. R01’s task flag concerns a generic completeness notice despite untruncated expected sections. R06’s rationale misstates which contact was shown; its task flag concerns contact coverage. R03’s fidelity flag concerns label-precaution wording. Scores are retained unchanged. Ten development controls matched expectations. Known cases, one answer each, bounded references and same-family grading limit interpretation. No clinician review or manual overrides occurred.')
d.paragraphs[72].paragraph_format.space_before=Pt(6)
setp(78,'Historical evidence and source lineage')
setp(79,'The preceding .9 answers, regraded with v3, had research fidelity 20/21 and tasks 20/21; paired tasks MCP 6/7 and plain 0/7. The fresh .10 run keeps the cases and grader, but changes application code and instructions and repeats live retrieval. Differences also reflect model and source variability; they are not a controlled causal estimate. Older .5 results (531 tests, research tasks 18/21, paired MCP 5/7) remain historical. Demos illustrate .4. Prior captures and raw grades are preserved.')
setp(80,'Databricks delivery and traceability')
setp(81,'Changes are in this submission folder’s server and chat-client directories. Local MCP .10 is not deployed; the mcp-mc Databricks app remains .9 with its prior deployment ID. Tests, Inspector and evaluation drivers ran locally; models and MLflow used existing Databricks services. No infrastructure, permissions, app deployment or GitHub upload changed. Evidence and readbacks are in evaluation/abstract-disclosure-revision. No production-readiness or clinical-certification claim is made.')
t=next(t for t in d.tables if t.cell(0,0).text=='Current measure')
values=[('Server unit tests','592 passed','Final local source; no skips'),('Evaluator unit tests','30 passed','Unchanged grader v3'),('Fresh chats',f'{C["completed"]["passed"]}/28','New answers and live retrieval'),('Expected routes',f'{C["boundary_behavior"]["passed"]}/28','Fresh trace checks'),('Tool checks',f'{C["tool_selection"]["passed"]}/28','Required/allowed selections'),('Fixed stops',f'{C["fixed_stops"]["passed"]}/7','Zero downstream calls'),('URL membership',f'{C["citation_provenance"]["passed"]}/21','Membership is not claim support'),('Research grades',f'{G["fidelity_pass"]} fidelity passes; {G["task_fulfilled"]}/21 tasks','Separate fallible model judgments')]
assert len(t.rows)-1==len(values)
for row,vals in zip(t.rows[1:],values):
 for cell,value in zip(row.cells,vals):
  p=cell.paragraphs[0]
  if p.runs:
   p.runs[0].text=value
   for run in p.runs[1:]:run.text=''
  else:p.add_run(value)
for rel in d.part.rels.values():
 if rel.is_external and 'evaluation/grader-attribution-revision/' in rel.target_ref:rel._target=rel.target_ref.replace('evaluation/grader-attribution-revision/','evaluation/abstract-disclosure-revision/')
d.save(W/'evaluation-updated.docx');print('Updated existing evaluation DOCX.')
