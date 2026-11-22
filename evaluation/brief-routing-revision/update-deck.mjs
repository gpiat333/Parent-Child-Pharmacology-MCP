import fs from 'node:fs/promises';
import {PresentationFile,FileBlob} from '@oai/artifact-tool';
const W='C:/Users/piatkowskigs/Desktop/.submission-brief-routing-review';
const P='C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20';
const S=JSON.parse(await fs.readFile(P+'/evaluation/brief-routing-revision/summary.json','utf8'));
const C=S.chat.counts,G=S.chat.diagnostic_grading,B=S.paired;
const p=await PresentationFile.importPptx(await FileBlob.load(W+'/reference.pptx'));
const inspected=await p.inspect({kind:'slide,textbox,shape,table',maxChars:300000});
const slides=new Map(inspected.records.filter(x=>x.kind==='slide').map(x=>[x.slideIndex+1,p.resolve(x.id)]));
const table=(n)=>p.resolve(inspected.records.find(x=>x.kind==='table'&&x.slideIndex===n-1).id);
function set(n,name,value){const x=slides.get(n).shapes.items.find(s=>s.name===name);if(!x)throw Error(`Missing ${n} ${name}`);x.text.replace(x.text.toString(),value);}
function cell(n,r,c,value){const x=table(n).getCell(r,c).text;x.replace(x.toString(),String(value));}
for(const [n,s] of slides){
  for(const sh of s.shapes.items){const old=sh.text.toString(),next=old.replaceAll('445','473').replaceAll('104 source files','106 source files');if(old!==next)sh.text.replace(old,next);}
  for(const t of s.tables.items){const snap=t.toSnapshot();for(let r=0;r<snap.rows;r++)for(let c=0;c<snap.cols;c++){const text=t.getCell(r,c).text,old=text.toString(),next=old.replaceAll('445','473').replaceAll('104 source files','106 source files');if(next!==old)text.replace(old,next);}}
  const notes=s.speakerNotes.text.toString();s.speakerNotes.text=notes.replaceAll('evaluation/program-safety-revision/','evaluation/brief-routing-revision/').replaceAll('445 tests','473 tests');
}
set(13,'metric-0',String(S.local_tests.tests));set(13,'metric-1',`${C.completed.passed}/28`);set(13,'metric-2',`${C.fixed_stops.passed}/7`);
set(13,'evaluation-details',`30 tools, 4 prompts and 4 resources.\nExpected routes: ${C.boundary_behavior.passed}/28. Required/allowed tools: ${C.tool_selection.passed}/28.\nExplicit brief requests now require the composite tool first.\nThe same 28 cases and seven paired questions were rerun.`);
cell(14,1,1,`${B.mcp.completed}/7`);cell(14,1,2,`${B.plain.completed}/7`);cell(14,2,1,`${B.mcp.task_fulfilled}/7`);cell(14,2,2,`${B.plain.task_fulfilled}/7`);
set(14,'limits','Only the MCP arm has tools and enforces the brief workflow.\nThe questions and grader match the prior 445-test run.\nKnown cases, one sample and a same-family judge limit comparison.\nA workflow pass does not establish clinical answer quality.');
set(17,'body-0','The companion screens the actual question before model execution. Stops suppress research and participation.');
set(17,'body-1','Explicit brief requests require the composite first. Other requests use automatic tool selection. Schemas validate arguments.');
set(40,'footer','Safety stops take priority over the requested brief workflow. Every client must enforce the contract.');
cell(40,4,1,`${C.boundary_behavior.passed}/28 expected routes. Seven intended stops made zero downstream calls.`);
cell(42,1,1,'106 source files frozen before the rerun. 473 unit tests pass.');
cell(42,2,1,'Same 28 questions, allowed/required tools and grading criteria as the prior 445-test run.');
cell(42,3,1,'Same model and shared instructions. MCP has tools and workflow enforcement; plain has no retrieval.');
cell(43,1,1,`${C.completed.passed}/28 completed; ${C.boundary_behavior.passed}/28 expected routes`);
cell(43,2,1,`${C.tool_selection.passed}/28 required/allowed checks. Original E01 check passes.`);
cell(43,3,1,`${C.fixed_stops.passed}/7; zero downstream evidence/model calls`);
cell(43,4,1,`${C.citation_provenance.passed}/21 research answers`);
cell(43,5,1,`${G.fidelity_pass} fidelity pass, ${G.fidelity_fail} fail, ${G.fidelity_not_assessable} not assessable; ${G.task_fulfilled}/21 tasks fulfilled`);
for(const [col,arm] of [[1,'mcp'],[2,'plain']]){cell(44,1,col,`${B[arm].completed}/7`);cell(44,2,col,`${B[arm].task_fulfilled}/7`);cell(44,3,col,`${B[arm].fidelity_pass} / ${B[arm].fidelity_fail} / ${B[arm].fidelity_not_assessable}`);cell(44,4,col,B[arm].median_seconds);}
set(44,'footer','Successful-attempt timings exclude the archived timeout and retry delay. No speed superiority is established.');
set(45,'Title','Brief workflow correction and remaining limits');
const rows=[['Cause','The prior daridorexant answer used individual tools and skipped the required composite evidence brief.'],['Correction','After an allowed preflight, the client requires the composite first. Safety and identity stops still take priority.'],['Verification',`E01 now calls the composite first. All ${S.workflow_requirements.length} explicit brief requests honor the contract. Cases and grading rules are unchanged.`],['Remaining limits',`${G.fidelity_fail} research answers failed fidelity checks; ${21-G.task_fulfilled} tasks were not fulfilled. Clinical review is still needed.`]];
rows.forEach(([a,b],i)=>{set(45,'label-'+i,a);set(45,'body-'+i,b);});
set(45,'footer','This fixes workflow execution. It does not prove better autonomous selection or clinical accuracy.');
slides.get(45).speakerNotes.text='Cause: evaluation/program-safety-revision/chats/E01-gap-results.json and chat-checks.json. Current verification: evaluation/brief-routing-revision/chats/E01-gap-results.json, summary.json and workflow-probes/. Same cases and grader v2 retained. The companion uses a named-tool requirement from preflight, then allows optional tools. No clinical adjudication. Current failures and full raw rationales remain in grading-review.json. A model-gateway timeout attempt was retained before retrying only the incomplete pair.';
const history=[['Current version','473 tests, 30 tools, 28 chats and seven pairs. Explicit brief requests now require the composite first.'],['Previous version','445 tests and 27/28 tool checks. The skipped E01 composite and all raw grades remain unchanged.'],['Earlier runs','443, 395, 359 and 301-test runs remain historical with their retained evidence. Remote checks do not validate this version.'],['Model access','The existing managed route worked. No credential renewal, provider change, deployment or GitHub push.']];
history.forEach(([a,b],i)=>{set(47,'label-'+i,a);set(47,'body-'+i,b);});
for(const [n,id] of [[5,'cross-source'],[6,'identity'],[7,'crisis'],[8,'gap'],[48,'questions'],[49,'empty']]){
  const im=slides.get(n).images.items[0];if(!im)throw Error('Demo image missing '+n);
  im.replace({blob:new Uint8Array(await fs.readFile(P+'/presentation/current-demo/'+id+'.png')),contentType:'image/png',alt:'Current saved response: '+id});
}
const map={main:15,appendix:34,total:49,slides:[...slides].map(([n,s])=>({slide:n,title:s.shapes.items.find(x=>x.name==='Title')?.text.toString()??'Parent-child Pharmacology MCP',hidden:s.hidden,nativeTables:s.tables.items.length}))};
await fs.writeFile(W+'/slide-map.json',JSON.stringify(map,null,2));
await(await PresentationFile.exportPptx(p)).save(W+'/professional-draft.pptx');
console.log('Updated the imported 49-slide deck in place.');process.exit(0);
