import fs from 'node:fs/promises';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const W='C:/Users/piatkowskigs/Desktop/.submission-notice-citation-review';
const P='C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20';
const S=JSON.parse(await fs.readFile(P+'/evaluation/notice-citation-revision/summary.json','utf8'));
const C=S.chat.counts,G=S.chat.diagnostic_grading,B=S.paired;
const p=await PresentationFile.importPptx(await FileBlob.load(W+'/reference.pptx'));
const inspected=await p.inspect({kind:'slide,textbox,shape,table',maxChars:300000});
const slides=new Map(inspected.records.filter(x=>x.kind==='slide').map(x=>[x.slideIndex+1,p.resolve(x.id)]));
const table=n=>p.resolve(inspected.records.find(x=>x.kind==='table'&&x.slideIndex===n-1).id);
function set(n,name,value){const x=slides.get(n).shapes.items.find(s=>s.name===name);if(!x)throw Error(`Missing ${n} ${name}`);x.text.replace(x.text.toString(),value);}
function cell(n,r,c,value){const x=table(n).getCell(r,c).text;x.replace(x.toString(),String(value));}
for(const [n,s] of slides){
  for(const sh of s.shapes.items){const old=sh.text.toString(),next=old.replaceAll('473','508').replaceAll('106 source files','112 source files');if(old!==next)sh.text.replace(old,next);}
  for(const t of s.tables.items){const snap=t.toSnapshot();for(let r=0;r<snap.rows;r++)for(let c=0;c<snap.cols;c++){const text=t.getCell(r,c).text,old=text.toString(),next=old.replaceAll('473','508').replaceAll('106 source files','112 source files');if(old!==next)text.replace(old,next);}}
  s.speakerNotes.text=s.speakerNotes.text.toString().replaceAll('evaluation/brief-routing-revision/','evaluation/notice-citation-revision/').replaceAll('473 tests','508 tests');
}
set(13,'metric-0','508');set(13,'metric-1',`${C.completed.passed}/28`);set(13,'metric-2',`${C.fixed_stops.passed}/7`);
set(13,'evaluation-details',`30 tools, 4 prompts and 4 resources.\nExpected routes: ${C.boundary_behavior.passed}/28. Required/allowed tools: ${C.tool_selection.passed}/28.\nRequired caveats now survive final-answer generation.\nThe same 28 cases and seven paired questions were rerun.`);
cell(14,1,1,`${B.mcp.completed}/7`);cell(14,1,2,`${B.plain.completed}/7`);cell(14,2,1,`${B.mcp.task_fulfilled}/7`);cell(14,2,2,`${B.plain.task_fulfilled}/7`);
set(14,'limits','Only MCP has tools, workflow enforcement and fixed notices.\nQuestions and grader match the prior 473-test run.\nKnown cases, one sample and a same-family judge limit comparison.\nMandatory caveats do not establish clinical answer quality.');
set(17,'body-3','The client retains source links and scope, renders required notices, and provides clinician preparation questions.');
cell(19,4,0,'RxNorm /\nMedlinePlus');
set(40,'footer','Safety stops take priority. Every client must enforce workflow and required-notice contracts.');
cell(40,4,1,`${C.boundary_behavior.passed}/28 expected routes. Seven intended stops made zero downstream calls.`);
cell(42,1,1,'112 source files frozen before the rerun. 508 unit tests pass.');
cell(42,2,1,'Same 28 questions, allowed/required tools and grading criteria as the prior 473-test run.');
cell(42,3,1,'Same model and shared instructions. MCP adds retrieval, workflow enforcement and fixed notices.');
cell(42,4,1,'Separate execution, corrected URL-membership checks and fallible diagnostic model judgments.');
cell(43,1,1,`${C.completed.passed}/28 completed; ${C.boundary_behavior.passed}/28 expected routes`);
cell(43,2,1,`${C.tool_selection.passed}/28 required/allowed checks`);
cell(43,3,1,`${C.fixed_stops.passed}/7; zero downstream evidence/model calls`);
cell(43,4,1,`${C.citation_provenance.passed}/21 research answers; corrected URL extraction`);
cell(43,5,1,`${G.fidelity_pass} fidelity pass, ${G.fidelity_fail} fail, ${G.fidelity_not_assessable} not assessable; ${G.task_fulfilled}/21 tasks fulfilled`);
set(43,'footer','Historical raw URL scores are unchanged. URL membership does not establish support for a claim.');
for(const [col,arm] of [[1,'mcp'],[2,'plain']]){cell(44,1,col,`${B[arm].completed}/7`);cell(44,2,col,`${B[arm].task_fulfilled}/7`);cell(44,3,col,`${B[arm].fidelity_pass} / ${B[arm].fidelity_fail} / ${B[arm].fidelity_not_assessable}`);cell(44,4,col,B[arm].median_seconds);}
set(44,'footer','Successful-attempt timings exclude incomplete attempts and retry delays. No speed superiority is established.');
set(45,'Title','Required caveats and citation parsing');
const rows=[['Cause','Two answers omitted required caveats. The URL checker merged adjacent Markdown citations.'],['Correction','The client renders fixed activity-code and clinical-review notices. The checker separates adjacent links.'],['Verification',`P01 and S6-pregnancy include their notices. R12 passes the parser regression. All ${S.required_notice_records} applicable chat notices are preserved.`],['Remaining limits',`Raw grader labels: ${G.fidelity_fail} fidelity failure and ${21-G.task_fulfilled} unmet tasks. These labels can be wrong. Clinical review is still needed.`]];
rows.forEach(([a,b],i)=>{set(45,'label-'+i,a);set(45,'body-'+i,b);});
set(45,'footer','The D05 grader appears to confuse study counts with doses. Raw grades remain; no clinician adjudication occurred.');
slides.get(45).speakerNotes.text='Cause: evaluation/brief-routing-revision/grading-review.json and url-parser-review.json. Current evidence: evaluation/notice-citation-revision/summary.json, notice-contract-checks.json and url-checker-regression.json. Required notices are selected by tool identity from trusted local policy, after generation. Before-notice answers and notice IDs are retained. The paired MCP arm uses the same renderer; plain has no appended notices. Questions and grader v2 remain unchanged. URL extraction changed, not the claim-support rubric. Historical raw scores are preserved. No clinician adjudication.';
slides.get(45).speakerNotes.text += ' Technical review: D05 quotes participant counts as dose evidence although no medication-dose values were found in the final answer; other study-design comments remain reviewable. P01 now contains its caveat; its current failure concerns a missing FY2024 group in capped results. The grader also labels application policy as an uncited source claim. E01 needs review of spontaneous-signal disclosure versus confirmed pregnancy outcomes. The paired E01 output retains dose-bearing animal details and reaction-count alignment concerns. Technical observations are in grading-review.json; no raw grades were adjusted. These fixes do not establish clinical safety or better raw-model reasoning.';
const history=[['Current version','508 tests, 30 tools, 28 chats and seven pairs. Fixed notices and corrected citation boundaries.'],['Previous version','473 tests; 28/28 tool checks; 19/21 tasks. Its two missed caveats and raw 20/21 URL score remain historical.'],['Earlier runs','445, 443, 395, 359 and 301-test runs retain their evidence. Remote checks do not validate this version.'],['Model access','Existing managed access was used. No credential renewal, provider change, deployment or GitHub push.']];
history.forEach(([a,b],i)=>{set(47,'label-'+i,a);set(47,'body-'+i,b);});
for(const [n,id] of [[5,'cross-source'],[6,'identity'],[7,'crisis'],[8,'gap'],[48,'questions'],[49,'empty']]){
 const im=slides.get(n).images.items[0];if(!im)throw Error('Demo image missing '+n);
 im.replace({blob:new Uint8Array(await fs.readFile(P+'/presentation/current-demo/'+id+'.png')),contentType:'image/png',alt:'Current saved response: '+id});
}
const map={main:15,appendix:34,total:49,slides:[...slides].map(([n,s])=>({slide:n,title:s.shapes.items.find(x=>x.name==='Title')?.text.toString()??'Parent-child Pharmacology MCP',hidden:s.hidden,nativeTables:s.tables.items.length}))};
await fs.writeFile(W+'/slide-map.json',JSON.stringify(map,null,2));
await(await PresentationFile.exportPptx(p)).save(W+'/professional-draft.pptx');
console.log('Updated the imported 49-slide deck.');process.exit(0);
