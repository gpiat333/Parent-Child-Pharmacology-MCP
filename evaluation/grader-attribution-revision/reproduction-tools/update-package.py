from pathlib import Path
import json,shutil,html,re
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/grader-attribution-revision'
S=json.loads((R/'summary.json').read_text(encoding='utf-8-sig'));C=S['chat']['counts'];G=S['chat']['diagnostic_grading'];B=S['paired']
backup=R/'prior-front-matter';backup.mkdir(exist_ok=True)
def write(relative,text):
 p=P/relative;b=backup/relative
 if p.exists() and not b.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
 p.write_text(text,encoding='utf-8')
state='This revision changes the grader and submission documents only. The existing **mcp-mc Databricks sandbox app remains on policy .9 and its prior deployment**. No app deployment, infrastructure or permission change, GitHub upload or official submission occurred. Tests and the replay driver ran locally; grader calls and MLflow used the existing Databricks services.'
fix='Grader v3 fixes E01 source-to-answer misattribution. Negative content findings must quote the candidate answer; omissions must identify a requested requirement. Stable citation IDs bind to original answer URLs. Cached scores must match the grader code, model and exact inputs. The first structurally valid judgment is retained, including failures. Up to two correction attempts are allowed only for invalid schema or attribution; raw attempts remain available. No manual pass overrides were made.'
counts='Fresh local tests: **562 server tests and 30 separate grader tests passed**, with zero failures, errors or skips. All **10 synthetic development controls** matched fidelity and task expectations. These controls are not held-out or clinical validation. All 114 frozen application files are unchanged; 93 runtime files were verified during the prior .9 deployment. The prior inventory of 30 tools, four prompts and four resources is unchanged and was not re-probed this revision.'
chats=f'All **42 retained rows** were reevaluated and read back in MLflow with zero scorer execution errors. No answer or source retrieval was regenerated. Retained chats: **{C["completed"]["passed"]}/28 completed**, {C["boundary_behavior"]["passed"]}/28 expected routes and {C["tool_selection"]["passed"]}/28 tool checks. Seven fixed stops contain zero downstream evidence/model calls. URL membership: {C["citation_provenance"]["passed"]}/21 research answers.'
fail_label='failure' if G['fidelity_fail']==1 else 'failures'
grades=f'Current grader v3 research results: **{G["fidelity_pass"]}/21 fidelity passes**, {G["fidelity_fail"]} {fail_label}, {G["fidelity_not_assessable"]} N/A; **{G["task_fulfilled"]}/21 tasks fulfilled**. Paired tasks: **MCP {B["mcp"]["task_fulfilled"]}/7, plain model {B["plain"]["task_fulfilled"]}/7**. Paired fidelity pass/fail/N/A: MCP {B["mcp"]["fidelity_pass"]}/{B["mcp"]["fidelity_fail"]}/{B["mcp"]["fidelity_not_assessable"]}; plain {B["plain"]["fidelity_pass"]}/{B["plain"]["fidelity_fail"]}/{B["plain"]["fidelity_not_assessable"]}.'
e01='E01 main now passes. The paired E01 answer still omits the required disclosure of absent abstracts, so that genuine task failure remains. The false dose allegations have been removed without modifying either answer.'
meaning='Fidelity means support in the captured reference pool; task fulfillment means meeting requested output requirements. These are separate, fallible model judgments. A supported answer can omit a required item, and an honest abstention can leave a lookup incomplete. N/A is excluded from fidelity rates. Literal quote validation and URL membership do not prove claim support or clinical safety.'
limits='This is a controlled grader replay of the same answers and evidence, not a new sample or improvement in model behavior. Known development cases, one retained answer each, bounded shared references and a same-family judge limit interpretation. Only MCP originally had retrieval, workflow enforcement and fixed notices. No clinician adjudication or new latency comparison was performed. Initial grader candidates, raw attempts and all current negative grades are preserved.'
history='Historical grader v2 on these same .9 answers reported research fidelity 21/21, tasks 20/21, and paired tasks MCP 6/7, plain 1/7. It contained the E01 attribution error. The older .5 runtime reported 531 tests, research tasks 18/21 and paired MCP 5/7, plain 0/7. Other intermediate runs remain archived. Saved demos illustrate .4; their scores and deployment statements describe that recording, not the present revision.'
report='evaluation/grader-attribution-revision/REPORT.md'
root=(P/'README.md').read_text(encoding='utf-8')
research=root.split('## Research and evidence contracts')[1].split('## Run and evidence locations')[0].strip()
write('README.md',f'''# Parent-child Pharmacology MCP

**Dataset Access Server** prototype for the GSA hackathon, supporting public-evidence discovery and clinician preparation for parents, clinicians, researchers and NICHD program staff.

**THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.**

{state} NIHRePORTERAgent source was not modified.

Start with [the package index](START_HERE.html), [updated deck](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx), [evaluation DOCX](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx), [current report]({report}) and [MLflow run]({S['mlflow']['parent']['url']}).

## Grader correction and verified results

{fix}

{counts}

{chats}

{grades}

{e01}

## What the grades mean

{meaning}

{limits}

{history} The deck has 49 slides: 15 main and 34 hidden appendix slides.

## Research and evidence contracts

{research}

## Run and evidence locations

Use `server/run-local.ps1 -Test` for local regressions or `server/run-local.ps1` for loopback serving. Existing app: [mcp-mc]({S['app_url']}). Unchanged deployment: `{S['deployment_id']}`. Policy: `{S['policy_version']}`; grader: `{S['grader_version']}`.

Changes for this request are in `evaluation/grader-attribution-revision`; `server` and `chat-client` application code is unchanged. See [grader changes](evaluation/grader-attribution-revision/grader-changes.diff), [capture lineage](evaluation/grader-attribution-revision/capture-lineage.json), [current implementation](documentation/CURRENT_IMPLEMENTATION.md), [Databricks validation](documentation/DATABRICKS_VALIDATION.md) and [technical review](evaluation/grader-attribution-revision/TECHNICAL_REVIEW.md). Original tool traces are artifacts; each replay row has one root span. Historical evidence remains preserved. No GitHub destination has been selected.
''')
links=[('Updated PowerPoint','presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx'),('Updated evaluation DOCX','documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx'),('Current evaluation and grading limits','evaluation/grader-attribution-revision/index.html'),('MLflow run',S['mlflow']['parent']['url']),('Historical demonstration','presentation/current-demo/index.html')]
write('START_HERE.html','<!doctype html><meta charset="utf-8"><title>Parent-child Pharmacology MCP submission</title><style>body{font:20px/1.5 Arial;max-width:1050px;margin:50px auto;color:#203849}a{color:#006b93}.notice{color:#b4232c;font-weight:bold}li{margin:12px 0}</style><h1>Parent-child Pharmacology MCP</h1><p class="notice">GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.</p>'+''.join('<p>'+html.escape(t.replace('**',''))+'</p>' for t in [state,counts,chats,grades,e01,meaning,limits])+'<ul>'+''.join('<li><a href="'+html.escape(url)+'">'+html.escape(label)+'</a></li>' for label,url in links)+'</ul>')
for name,title in [('DATABRICKS_VALIDATION.md','Databricks validation'),('CURRENT_IMPLEMENTATION.md','Current implementation')]:
 previous=(P/'documentation'/name).read_text(encoding='utf-8')
 contract='\n\n## Outcome and report-context contract\n\n'+previous.split('## Outcome and report-context contract')[1].split('[Full report]')[0].strip() if '## Outcome and report-context contract' in previous else ''
 write('documentation/'+name,'# '+title+'\n\n'+'\n\n'.join([state,fix,counts,chats,grades,e01,meaning,limits])+contract+f'\n\n[Full report](../{report}). [MLflow run]({S["mlflow"]["parent"]["url"]}).\n')
write('presentation/README.md','# Presentation and demonstration\n\nThe updated deck has 49 slides: 15 main and 34 hidden appendix slides. The exact red title disclaimer and six safety risks remain.\n\n'+'\n\n'.join([state,chats,grades,e01,meaning,limits,history])+'\n\nCurrent validation: [evaluation report](../'+report+'). Prior deck and DOCX files are archived.\n')
# This README is documentation, excluded from the 114-file application freeze.
write('server/README.md','# Parent-child Pharmacology MCP server\n\nApplication code remains on policy 2026-11-21.9. This revision changed only grader code and submission documents; no app deployment or GitHub upload occurred. Fresh server suite: 562 tests pass. The separate grader suite has 30 passing tests. See ../README.md, ../documentation/CURRENT_IMPLEMENTATION.md and ../evaluation/grader-attribution-revision/REPORT.md. Run run-local.ps1 with -Test for local server tests.\n')
for p in sorted((P/'documentation').glob('*.md')):
 if p.name in {'DATABRICKS_VALIDATION.md','CURRENT_IMPLEMENTATION.md'}:continue
 content=re.sub(r'^> Current status[^\n]*\n\n','',p.read_text(encoding='utf-8-sig'))
 write(str(p.relative_to(P)),'> Current status: policy .9 is unchanged; grader v3 replays the same answers and evidence. 562 server and 30 evaluator tests pass locally. No deployment or GitHub upload in this revision. See [current validation](DATABRICKS_VALIDATION.md). Earlier counts and deployment statements below are historical.\n\n'+content)
viewer=P/'presentation/current-demo/index.html'
text=re.sub(r'<header>.*?</header>','<header>GSA prototype · Historical local demo from .4 · <a style="color:white" href="../../evaluation/grader-attribution-revision/index.html">Current grader v3 replay of .9 answers</a></header>',viewer.read_text(encoding='utf-8'),count=1,flags=re.S)
write('presentation/current-demo/index.html',text)
for name in ['NARRATION.md','GAP_DEMO_SCRIPT.md']:
 p=P/'presentation/current-demo'/name;content=re.sub(r'^> Historical[^\n]*\n\n','',p.read_text(encoding='utf-8-sig'))
 write(str(p.relative_to(P)),'> Historical local demo from .4. Grader v3 replays retained .9 answers; no new demo was recorded. See [current validation](../../evaluation/grader-attribution-revision/REPORT.md).\n\n'+content)
write('PACKAGING.md','# Submission package\n\n'+state+'\n\n'+counts+'\n\nThe deck has 49 slides: 15 main and 34 hidden appendix. The evaluation DOCX was rendered and reviewed. Prior artifacts and raw evaluations are retained. Current verification: evaluation/grader-attribution-revision/final-validation.json and evidence-manifest.json; package hashes: SHA256SUMS.txt. Demo media remain historical .4 captures.\n')
results_source=backup/'evaluation/results.json'
if not results_source.exists():results_source=P/'evaluation/results.json'
results=json.loads(results_source.read_text(encoding='utf-8-sig'))
entry={'revision':'report_context_v2_before_grader_fix','report':'report-context-revision/REPORT.md','summary':'report-context-revision/summary.json','deployed':True,'historical_grader':'v2'}
if not any(isinstance(x,dict) and x.get('revision')==entry['revision'] for x in results['historical_evidence']):results['historical_evidence'].append(entry)
results['current_revision']=S;results['current_report']='grader-attribution-revision/REPORT.md'
write('evaluation/results.json',json.dumps(results,indent=2,ensure_ascii=False))
print('Updated current package entry points; historical raw evidence preserved.')
