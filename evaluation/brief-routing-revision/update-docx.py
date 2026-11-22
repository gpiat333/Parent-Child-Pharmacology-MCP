from pathlib import Path
import json
from docx import Document
from docx.oxml.ns import qn
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/brief-routing-revision'
S=json.loads((R/'summary.json').read_text(encoding='utf-8'));C=S['chat']['counts'];G=S['chat']['diagnostic_grading'];B=S['paired']
d=Document(W/'reference.docx')
def setp(i,text):
    p=d.paragraphs[i]
    # Keep paragraph style, spacing and page-break properties from the GSA template.
    if p.runs:
        p.runs[0].text=text
        for run in p.runs[1:]:run.text=''
    else:p.add_run(text)
setp(2,f'The local prototype passes 473 unit tests. The rerun completed {C["completed"]["passed"]}/28 chats with {C["tool_selection"]["passed"]}/28 required/allowed tool checks. Seven paired questions produced 14 answers. This revision fixes a skipped evidence-brief workflow while preserving safety stops. Nothing was deployed or pushed.')
setp(19,'473 unit tests passed with zero failures, errors or skips. The current freeze contains 106 server and companion files. The local MCP exposes 30 tools, four prompts and four resources. Twenty direct protocol probes cover the existing 17 source/contract checks and three new workflow checks. The 28 added unit cases cover explicit and negated requests, priority of stops, missing tools and rejected bypasses.')
setp(21,'The same 28 questions from the preceding 445-test run are retained, including the portfolio query, count-only coverage query and two clinical-framing prompts. Seven intended stops are assessed as fixed contracts. The other 21 cases receive diagnostic model grades against their retrieved evidence. Required/allowed-tool checks and source-URL membership are assessed separately from clinical interpretation.')
setp(22,'Workflow correction and retained retries')
setp(23,'The prior 445-test run had 27/28 tool checks: E01 used individual retrieval tools instead of the required composite. Its answer received a diagnostic task pass, but the workflow was skipped. The client now requires the composite first after an allowed preflight. The original E01 question passes. Completed rerun answers are retained unchanged. A paired model-gateway timeout attempt was archived before retrying only that incomplete answer.')
setp(25,'Both arms use the same model and shared instructions, once per question. Only MCP receives tools and enforces the preflight workflow requirement. The plain arm has no retrieval. A shared bounded reference pool is judged without arm labels. The paired runner uses a shorter prompt than the production companion and its source-review stage. Timings include service and retrieval effects under parallel load.')
setp(42,'Framing evaluations')
setp(43,'Two retained cases ask for balanced sertraline lactation and lamotrigine pregnancy research summaries. Their criteria check source context, population and outcome distinctions, unsupported reassurance and medication-change advice. Raw answers and diagnostic grades are retained. These prompts are development cases, not proof that the system avoids alarm. S6 remains partially addressed and requires clinician review together with S2.')
setp(60,'Safety and workflow routing')
setp(61,'Whole-question safety, identity, privacy and language checks run before workflow routing. Explicit English brief requests then require medication_evidence_brief before optional tools or a final answer. A missing tool or bypass attempt fails closed. Language thresholds are unchanged and can still overblock short technical English. Incidental or negated brief mentions do not activate the workflow. Every third-party client must enforce the contract.')
setp(69,f'Seven paired questions produced MCP {B["mcp"]["completed"]}/7 and plain {B["plain"]["completed"]}/7 completed answers. Diagnostic task labels were MCP {B["mcp"]["task_fulfilled"]}/7 and plain {B["plain"]["task_fulfilled"]}/7. Only MCP has retrieval tools and workflow enforcement. Honest inability can leave a lookup incomplete without being false. Median times were {B["mcp"]["median_seconds"]} and {B["plain"]["median_seconds"]} seconds for successful attempts under parallel load, excluding the archived timeout and retry delay.')
setp(71,f'The 28 questions, grading criteria and grader v2 prompt match the prior 445-test run. Four synthetic controls matched {S["chat"]["calibration"]["fidelity_matches"]}/4 fidelity and {S["chat"]["calibration"]["task_matches"]}/4 task expectations. They do not validate clinical grading. Known cases, one new sample, live-source changes, same-family judging and bounded references limit comparison. No clinician adjudication occurred and raw labels remain unchanged. Workflow success is not improved autonomous selection or clinical answer quality.')
setp(72,f'E01 now passes with the composite called first. Diagnostic grading retains {G["fidelity_fail"]} fidelity failures and {21-G["task_fulfilled"]} unmet tasks: P01 omitted the activity-code caveat; S6-pregnancy omitted the explicit human-review statement. R12\'s URL regex joined adjacent links that occur separately in the tool output. The raw 20/21 score is retained. See grading-review.json for details. S2 and S6 still need clinical review.')
setp(79,'The prior 445-test run, including its 27/28 tool result, remains unchanged under evaluation/program-safety-revision with matching source snapshots. The 443, 395, 359 and 301-test runs and earlier remote checks are historical. They do not validate the current source. Existing managed model access was used. No credential renewal or provider configuration change occurred.')
for i,p in enumerate(d.paragraphs):
    if 'rate-limit attempts' in p.text:setp(i,p.text.replace('rate-limit attempts','incomplete infrastructure attempts'))
# The result table is identified by its existing heading, not by document table order.
t=next(t for t in d.tables if t.cell(0,0).text=='Current measure')
values=[('Unit tests','473 passed','Zero failures, errors or skips'),('Chat completion',f'{C["completed"]["passed"]}/28','Current final cases; earlier runs retained'),('Expected routes',f'{C["boundary_behavior"]["passed"]}/28','Same known evaluation cases'),('Tool checks',f'{C["tool_selection"]["passed"]}/28','Required/allowed selections'),('Fixed stops',f'{C["fixed_stops"]["passed"]}/7','Zero downstream evidence/model calls'),('URL provenance',f'{C["citation_provenance"]["passed"]}/21','URL membership, not claim support'),('Research grades',f'{G["fidelity_pass"]} fidelity passes; {G["task_fulfilled"]}/21 tasks','Fallible diagnostic model labels')]
for row,values in zip(t.rows[1:],values):
    for c,value in zip(row.cells,values):
        p=c.paragraphs[0]
        if p.runs:
            p.runs[0].text=value
            for run in p.runs[1:]:run.text=''
        else:p.add_run(value)
for rel in d.part.rels.values():
    if rel.is_external and 'evaluation/program-safety-revision/' in rel.target_ref:
        rel._target=rel.target_ref.replace('evaluation/program-safety-revision/','evaluation/brief-routing-revision/')
d.save(W/'evaluation-updated.docx')
print('Updated existing GSA evaluation document with current results.')
