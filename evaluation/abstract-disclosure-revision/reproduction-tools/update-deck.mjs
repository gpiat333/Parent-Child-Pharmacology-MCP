import fs from 'node:fs/promises';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const W='C:/Users/piatkowskigs/Desktop/.submission-abstract-disclosure-review';
const P='C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20';
const R=P+'/evaluation/abstract-disclosure-revision';
const S=JSON.parse(await fs.readFile(R+'/summary.json','utf8')),C=S.chat.counts,G=S.chat.diagnostic_grading,B=S.paired;
const p=await PresentationFile.importPptx(await FileBlob.load(W+'/reference.pptx'));
const inspected=await p.inspect({kind:'slide,textbox,shape,table',maxChars:300000});
await fs.writeFile(W+'/import-layout.json',JSON.stringify(await p.inspect({kind:'layout',maxChars:60000}),null,2));
const slides=new Map(inspected.records.filter(x=>x.kind==='slide').map(x=>[x.slideIndex+1,p.resolve(x.id)]));
const table=n=>p.resolve(inspected.records.find(x=>x.kind==='table'&&x.slideIndex===n-1).id);
function set(n,name,value){const x=slides.get(n).shapes.items.find(s=>s.name===name);if(!x)throw Error(`Missing ${n} ${name}`);x.text.replace(x.text.toString(),value);}
function cell(n,r,c,value){const x=table(n).getCell(r,c).text;x.replace(x.toString(),String(value));}
const changed=[5,6,7,8,13,14,15,34,40,42,43,44,45,46,47,48,49];
for(const n of changed)slides.get(n).speakerNotes.text='Current evidence: evaluation/abstract-disclosure-revision/REPORT.md and summary.json. Local MCP .10; deployed .9 unchanged. Fresh 28 chat captures and 14 paired answers, fresh live references, unchanged grader v3 and cases. Local unit tests, MCP Inspector and driver; existing Databricks model gateway and MLflow. No app deployment or GitHub upload. '+S.mlflow.parent.url+' . Known development questions, one answer per case/arm, same-family judge and no clinician adjudication. Read failures and limits aloud.';
set(13,'Title','Fresh local evaluation');
set(13,'metric-0',String(S.local_tests.tests));set(13,'metric-1',`${C.completed.passed}/28`);set(13,'metric-2',`${C.fixed_stops.passed}/7`);
set(13,'metric-label-0','server unit tests pass');set(13,'metric-label-1','fresh chats complete');set(13,'metric-label-2','fixed stops pass');
set(13,'evaluation-details',`30 grader tests; ${S.inspector.passed}/${S.inspector.checks} MCP Inspector checks pass.\n42 fresh capture rows scored and verified in Databricks MLflow.\nResearch: ${G.fidelity_pass}/21 fidelity; ${G.task_fulfilled}/21 tasks fulfilled.\nLocal MCP .10; unchanged grader v3 and evaluation questions.`);
set(13,'footer','MCP, tests and driver ran locally; model and tracking used Databricks. No deployment or clinical review.');
set(14,'Title','Fresh answers: MCP and plain model');
cell(14,1,0,'Fresh completed answers');cell(14,2,0,'Tasks fulfilled');
for(const [col,arm] of [[1,'mcp'],[2,'plain']]){cell(14,1,col,`${B[arm].completed}/7`);cell(14,2,col,`${B[arm].task_fulfilled}/7`);}
set(14,'limits','Same model and shared instructions; fresh answers and references.\nOnly MCP has retrieval, workflow enforcement and application notices.\nPaired MCP omits the companion’s extra model source-review pass.\nSeven known questions; same-family judge; no clinician review.');
set(14,'footer','A small workflow comparison; live sources and generated answers vary. No clinical accuracy or speed claim.');
set(15,'footer','Missing data never reads as safe. Test beyond known cases; independent clinical review remains necessary.');
cell(34,5,1,`${S.local_tests.tests} server tests pass. Local Inspector confirms 30 tool schemas and rejects a negative result limit.`);
cell(40,4,1,`Fresh traces: ${C.boundary_behavior.passed}/28 expected routes. Seven intended stops made zero downstream calls.`);
cell(40,5,1,'30 new tests cover abstract gaps, retrieval failures, combination products and Python/PowerShell disclosure parity.');
cell(42,1,1,`${S.source_files} application files frozen. Local tests: ${S.local_tests.tests} server + 30 grader. Inspector: ${S.inspector.passed}/${S.inspector.checks}.`);
cell(42,2,1,'Same 28 questions and criteria; new answers and live retrieval against local MCP .10.');
cell(42,3,1,'Seven fresh pairs; same model and shared instructions. MCP alone has retrieval and application enforcement.');
cell(42,4,1,'Unchanged grader v3: 35 model grades + seven fixed stops = 42 verified MLflow rows. No score overrides.');
set(42,'footer','Known development cases, one answer each, bounded references and no clinician adjudication.');
set(43,'Title','Fresh chats: execution and grading');
cell(43,1,1,`${C.completed.passed}/28 completed; ${C.boundary_behavior.passed}/28 expected routes`);
cell(43,2,1,`${C.tool_selection.passed}/28 required/allowed checks`);
cell(43,3,1,`${C.fixed_stops.passed}/7; zero downstream evidence/model calls`);
cell(43,4,1,`${C.citation_provenance.passed}/21 research answers; URL membership only`);
cell(43,5,1,`${G.fidelity_pass} fidelity pass, ${G.fidelity_fail} fail, ${G.fidelity_not_assessable} N/A; ${G.task_fulfilled}/21 tasks fulfilled`);
set(43,'footer','URL membership does not establish claim support. Fidelity and task completeness are separate model judgments.');
for(const [col,arm] of [[1,'mcp'],[2,'plain']]){cell(44,1,col,`${B[arm].completed}/7`);cell(44,2,col,`${B[arm].task_fulfilled}/7`);cell(44,3,col,`${B[arm].fidelity_pass} / ${B[arm].fidelity_fail} / ${B[arm].fidelity_not_assessable}`);cell(44,4,col,'7');}
cell(44,1,0,'Fresh completed answers');cell(44,4,0,'New answers generated');
set(44,'footer','N/A is excluded from fidelity rates. A shared bounded pool may contain evidence the plain answer never received.');
set(45,'Title','Make retrieval gaps visible');
const e=S.grading_rows.find(x=>x.case==='E01-gap'&&x.arm==='mcp');
const explanations=[['Payload','PMID-level coverage separates missing abstracts, unreturned records and failed lookups. Titles are not outcomes.'],['Client\ndisclosure','Both companion clients append the required gap notice. A later successful refetch updates the coverage.'],['Fresh E01',`Paired MCP: fidelity ${e.fidelity}; task ${e.task_fulfilled?'fulfilled':'not fulfilled'}. Full grades and any remaining omissions are preserved.`],['Grading limits','R01/R06 task flags concern completeness; one rationale misdescribes the answer. Scores remain unchanged for transparent review.']];
explanations.forEach(([a,b],i)=>{set(45,'label-'+i,a);set(45,'body-'+i,b);});
set(45,'footer','Other MCP clients must honor the payload display contract. No clinician adjudication or clinical certification.');
set(46,'body-0','Local MCP .10 contains the disclosure and grounding fixes. The existing OAuth-protected Databricks app remains on .9; this version has not been deployed.');
set(46,'footer','No app deployment, infrastructure or permission changes, GitHub upload or official submission in this revision.');
const history=[['Current .10',`Fresh local answers, grader v3: research fidelity ${G.fidelity_pass}/21, tasks ${G.task_fulfilled}/21; paired tasks MCP ${B.mcp.task_fulfilled}/7, plain ${B.plain.task_fulfilled}/7.`],['Previous .9','Prior answers, grader v3: research fidelity 20/21, tasks 20/21; paired tasks MCP 6/7, plain 0/7.'],['Earlier .5','Different runtime: 531 tests, research fidelity 21/21 and tasks 18/21; paired tasks MCP 5/7, plain 0/7.'],['Interpretation','New code and instructions, fresh sources and answers; same grader and cases. Differences are not a controlled causal estimate.']];
history.forEach(([a,b],i)=>{set(47,'label-'+i,a);set(47,'body-'+i,b);});
set(47,'footer','Current evidence: evaluation/abstract-disclosure-revision. Prior raw results preserved; no clinical review.');
for(const n of [5,6,7,8,48,49]){set(n,'footer','Historical saved demo from .4. Fresh local .10 evaluation results appear on slides 13–14 and in the appendix.');slides.get(n).speakerNotes.text+=' Image is a saved .4 demonstration. Full source responses: presentation/current-demo/index.html.';}
const map={main:15,appendix:34,total:49,changed,slides:[...slides].map(([n,s])=>({slide:n,title:s.shapes.items.find(x=>x.name==='Title')?.text.toString()??'Parent-child Pharmacology MCP',hidden:s.hidden,nativeTables:s.tables.items.length}))};
await fs.writeFile(W+'/slide-map.json',JSON.stringify(map,null,2));
await(await PresentationFile.exportPptx(p)).save(W+'/professional-draft.pptx');
console.log('Updated existing 49-slide deck.');process.exit(0);
