from pathlib import Path
import json,shutil,html,re
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision'
S=json.loads((R/'summary.json').read_text(encoding='utf-8'));C=S['chat']['counts'];G=S['chat']['diagnostic_grading'];B=S['paired'];backup=R/'prior-front-matter';backup.mkdir(exist_ok=True)
def write(relative,text):
 p=P/relative;b=backup/relative
 if p.exists() and not b.exists():b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
 p.write_text(text,encoding='utf-8')
state='The local MCP is now policy .10. The existing **mcp-mc Databricks sandbox app remains on policy .9 and its prior deployment**. No app deployment, infrastructure or permission change, GitHub upload or official submission occurred. Unit tests, MCP Inspector and evaluation drivers ran locally; model calls, grading and MLflow used existing Databricks services.'
fix='PubMed retrieval now returns PMID-level abstract coverage, separating missing text, unreturned records and request failures. The composite brief preserves the coverage. Both companion clients append a validated disclosure when needed, and a later successful refetch updates it. Titles alone are not outcome evidence. General instructions also preserve recall candidates and statuses, distinguish study comparators and unspecified specimens, and avoid unsupported methodological additions.'
counts=f'**592 server tests and 30 separate grader tests passed**, with zero failures, errors or skips. All **10 synthetic development controls** matched both grade dimensions. These are not held-out or clinical validation. The {S["source_files"]} final application files are frozen. **MCP Inspector: {S["inspector"]["passed"]}/{S["inspector"]["checks"]} checks**, including the inventory of 30 tools, four prompts and four resources.'
chats=f'All **42 fresh capture rows** were graded and read back in MLflow, with zero scorer execution errors. Chats: **{C["completed"]["passed"]}/28 completed**, {C["boundary_behavior"]["passed"]}/28 expected routes and {C["tool_selection"]["passed"]}/28 tool-selection checks. Seven fixed stops made zero downstream evidence/model calls. URL membership: {C["citation_provenance"]["passed"]}/21 research answers.'
grades=f'Current research results: **{G["fidelity_pass"]}/21 fidelity passes** ({G["fidelity_fail"]} fail, {G["fidelity_not_assessable"]} N/A); **{G["task_fulfilled"]}/21 tasks fulfilled**. Fresh paired task fulfillment: **MCP {B["mcp"]["task_fulfilled"]}/7; plain model {B["plain"]["task_fulfilled"]}/7**. Paired fidelity pass/fail/N/A: MCP {B["mcp"]["fidelity_pass"]}/{B["mcp"]["fidelity_fail"]}/{B["mcp"]["fidelity_not_assessable"]}; plain {B["plain"]["fidelity_pass"]}/{B["plain"]["fidelity_fail"]}/{B["plain"]["fidelity_not_assessable"]}.'
meaning='Fidelity measures support in the captured reference pool. Task fulfillment measures completion of requested requirements. They are separate, fallible model judgments: a supported answer can omit an item; an honest abstention can leave a lookup incomplete. N/A is excluded from fidelity rates. Literal quote checks and URL membership do not prove clinical truth or safety.'
limits='The evaluation cases and grader v3 core are unchanged; answers and tool-retrieved references are fresh, with normal source caches and snapshots. One answer per known development case, changing sources, model variability, a bounded shared pool and same-family grading limit interpretation. Only MCP has retrieval, workflow enforcement and notices. The main companion adds source review; the paired runner does not. R01 and R06 paired task flags concern completeness; R06’s rationale misdescribes which contact was shown. R03 has a label-wording fidelity flag. Scores remain unchanged for transparent review. No clinician adjudication or manual overrides occurred. This is a workflow comparison, not a clinical accuracy or speed claim.'
history='The previous .9 answers, regraded with v3, had research fidelity 20/21 and tasks 20/21; paired tasks MCP 6/7 and plain 0/7. The fresh .10 run changes application code and instructions as well as answers and live sources, so differences are not a controlled causal estimate. Older .5 figures (531 tests, research tasks 18/21 and paired MCP 5/7) remain historical. Prior raw evidence is preserved. Saved demo images and video illustrate .4.'
e=next(r for r in S['grading_rows'] if r['case']=='E01-gap' and r['arm']=='mcp');e01=f'Fresh paired E01: fidelity {e["fidelity"]}; task {"fulfilled" if e["task_fulfilled"] else "not fulfilled"}. The answer contains the required missing-abstract disclosure. All negative grades and rationales remain in the technical review.'
report='evaluation/abstract-disclosure-revision/REPORT.md';root=(P/'README.md').read_text(encoding='utf-8')
research=root.split('## Research and evidence contracts')[1].split('## Run and evidence locations')[0].strip()
write('README.md',f'''# Parent-child Pharmacology MCP

**Dataset Access Server** prototype for the GSA hackathon, supporting public-evidence discovery and clinician preparation for parents, clinicians, researchers and NICHD program staff.

**THIS MCP HAS BEEN MADE FOR THE PURPOSE OF THE GSA HACKATHON AS A PROTOTYPE AND IS NOT AN NIH OFFICIAL MCP TOOL. NO PRODUCTION READINESS CLAIM.**

{state} NIHRePORTERAgent source was not modified.

Start with [the package index](START_HERE.html), [updated deck](presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx), [evaluation DOCX](documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx), [current report]({report}) and [MLflow run]({S['mlflow']['parent']['url']}).

## Changes and verified results

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

Abstract disclosures are application metadata, not source-authored medical findings. Every client must preserve them. The bundled Python and PowerShell clients enforce them; an arbitrary third-party client may not.

## Run and evidence locations

Use `server/run-local.ps1 -Test` for local regressions or `server/run-local.ps1` for loopback serving. Existing app: [mcp-mc]({S['app_url']}). Unchanged deployed policy .9, deployment `{S['deployment_id']}`. Local source policy: `{S['policy_version']}`; grader: `{S['grader_version']}`.

Application changes are in this submission folder’s `server` and `chat-client`; fresh evaluation evidence is in `evaluation/abstract-disclosure-revision`. See [source changes](evaluation/abstract-disclosure-revision/source-changes.diff), [capture lineage](evaluation/abstract-disclosure-revision/capture-lineage.json), [implementation](documentation/CURRENT_IMPLEMENTATION.md), [Databricks validation](documentation/DATABRICKS_VALIDATION.md) and [technical review](evaluation/abstract-disclosure-revision/TECHNICAL_REVIEW.md). This version is not deployed. No GitHub destination has been selected.
''')
links=[('Updated PowerPoint','presentation/Parent-child%20Pharmacology%20MCP%20%E2%80%94%20Updated.pptx'),('Updated evaluation DOCX','documentation/Parent-child%20Pharmacology%20MCP%20-%20Evaluation.docx'),('Fresh evaluation and grading limits','evaluation/abstract-disclosure-revision/index.html'),('MLflow run',S['mlflow']['parent']['url']),('Historical demonstration','presentation/current-demo/index.html')]
style='<style>body{font:19px/1.5 Arial;max-width:1080px;margin:45px auto;color:#203849;padding:0 24px}a{color:#006b93}.notice{color:#b4232c;font-weight:bold}li{margin:12px 0}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ccd7df;padding:10px;text-align:left}</style>'
write('START_HERE.html','<!doctype html><meta charset="utf-8"><title>Parent-child Pharmacology MCP submission</title>'+style+'<h1>Parent-child Pharmacology MCP</h1><p class="notice">GSA hackathon prototype. Not an official NIH MCP tool. No production-readiness claim.</p>'+''.join('<p>'+html.escape(t.replace('**',''))+'</p>' for t in [state,counts,chats,grades,e01,meaning,limits])+'<ul>'+''.join('<li><a href="'+html.escape(url)+'">'+html.escape(label)+'</a></li>' for label,url in links)+'</ul>')
for name,title in [('DATABRICKS_VALIDATION.md','Databricks validation'),('CURRENT_IMPLEMENTATION.md','Current implementation')]:
 previous=(P/'documentation'/name).read_text(encoding='utf-8')
 contract='\n\n## Outcome and report-context contract\n\n'+previous.split('## Outcome and report-context contract')[1].split('[Full report]')[0].strip() if '## Outcome and report-context contract' in previous else ''
 write('documentation/'+name,'# '+title+'\n\n'+'\n\n'.join([state,fix,counts,chats,grades,e01,meaning,limits])+contract+f'\n\n[Full report](../{report}). [MLflow run]({S["mlflow"]["parent"]["url"]}).\n')
write('presentation/README.md','# Presentation and demonstration\n\n49 slides: 15 main and 34 hidden appendix slides. The exact red title disclaimer and six safety risks remain.\n\n'+'\n\n'.join([state,chats,grades,e01,meaning,limits,history])+'\n\nCurrent validation: [evaluation report](../'+report+'). Prior deck and DOCX versions are archived.\n')
write('server/README.md','# Parent-child Pharmacology MCP server\n\nLocal source policy 2026-11-21.10 adds abstract-coverage disclosure and improves source-grounding instructions. This version is not deployed. Server suite: 592 tests pass; separate unchanged grader suite: 30 tests pass. Local MCP Inspector: 9/9 checks. See ../README.md and ../evaluation/abstract-disclosure-revision/REPORT.md. Run run-local.ps1 with -Test for local tests.\n')
for p in sorted((P/'documentation').glob('*.md')):
 if p.name in {'DATABRICKS_VALIDATION.md','CURRENT_IMPLEMENTATION.md'}:continue
 content=re.sub(r'^> Current status[^\n]*\n\n','',p.read_text(encoding='utf-8-sig'))
 write(str(p.relative_to(P)),'> Current status: local policy .10, deployed .9 unchanged. Fresh chats and paired answers, unchanged grader v3. 592 server and 30 grader tests pass. No deployment or GitHub upload. See [current validation](DATABRICKS_VALIDATION.md). Earlier numbers and deployment statements below are historical.\n\n'+content)
viewer=P/'presentation/current-demo/index.html';text=re.sub(r'<header>.*?</header>','<header>GSA prototype · Historical local demo from .4 · <a style="color:white" href="../../evaluation/abstract-disclosure-revision/index.html">Fresh local .10 evaluation</a></header>',viewer.read_text(encoding='utf-8'),count=1,flags=re.S);write('presentation/current-demo/index.html',text)
for name in ['NARRATION.md','GAP_DEMO_SCRIPT.md']:
 p=P/'presentation/current-demo'/name;content=re.sub(r'^> Historical[^\n]*\n\n','',p.read_text(encoding='utf-8-sig'))
 write(str(p.relative_to(P)),'> Historical local demo from .4. Fresh local .10 evaluations are separate; no new video was recorded. See [current validation](../../evaluation/abstract-disclosure-revision/REPORT.md).\n\n'+content)
write('PACKAGING.md','# Submission package\n\n'+state+'\n\n'+counts+'\n\nThe deck has 49 slides: 15 main and 34 hidden appendix. The evaluation DOCX was rendered and reviewed. Prior artifacts and raw evaluations are retained. Current verification: evaluation/abstract-disclosure-revision/final-validation.json and evidence-manifest.json. Package hashes: SHA256SUMS.txt. Demo media remain historical .4 captures.\n')
results=json.loads((P/'evaluation/results.json').read_text(encoding='utf-8-sig'));entry={'revision':'grader_attribution_v3_previous','report':'grader-attribution-revision/REPORT.md','summary':'grader-attribution-revision/summary.json','deployed_this_revision':False,'historical':True}
if not any(isinstance(x,dict) and x.get('revision')==entry['revision'] for x in results['historical_evidence']):results['historical_evidence'].append(entry)
results['current_revision']=S;results['current_report']='abstract-disclosure-revision/REPORT.md';write('evaluation/results.json',json.dumps(results,indent=2,ensure_ascii=False))
review=''.join('<tr><td>'+html.escape(r['case']+' / '+r['arm'])+'</td><td>'+html.escape(r['fidelity'])+'</td><td>'+str(r['task_fulfilled'])+'</td><td>'+html.escape(r['rationale'])+'</td></tr>' for r in S['grading_rows'])
(R/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Fresh local MCP evaluation</title>'+style+'<h1>Fresh local MCP .10 evaluation</h1>'+''.join('<p>'+html.escape(t.replace('**',''))+'</p>' for t in [state,fix,counts,chats,grades,meaning,limits,history])+'<p><a href="REPORT.md">Full report</a> · <a href="summary.json">Machine-readable metrics</a> · <a href="'+S['mlflow']['parent']['url']+'">MLflow run</a></p><table><tr><th>Case / arm</th><th>Fidelity</th><th>Task fulfilled</th><th>Diagnostic rationale</th></tr>'+review+'</table>',encoding='utf-8')
print('Current documentation and entry points updated; prior material archived.')
