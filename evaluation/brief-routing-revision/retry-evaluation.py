from pathlib import Path
import json,sys,shutil,subprocess,time
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/brief-routing-revision'
sys.path.insert(0,str(R));import paired_evaluation as pe
phase=sys.argv[1]
events=pe.read(R/('retry-'+phase+'.json')) if (R/('retry-'+phase+'.json')).exists() else []
def event(x):
 events.append(x);pe.save(R/('retry-'+phase+'.json'),events);print(x,flush=True)
original=pe.model_call
def retry_model(*a,**kw):
 for attempt in range(4):
  try:return original(*a,**kw)
  except RuntimeError as e:
   if '429' not in str(e) or attempt==3:raise
   event({'action':'retry_grade','attempt':attempt+1,'http_status':429});time.sleep(60)
pe.model_call=retry_model
if phase=='chats':
 for c in pe.read(R/'cases.json'):
  f=R/'chats'/(c['id']+'-results.json')
  if f.exists() and pe.read(f).get('completed'):continue
  for attempt in range(1,5):
   archive=R/'infrastructure-attempts'/c['id']/str(attempt);archive.mkdir(parents=True,exist_ok=True)
   for old in (R/'chats').glob(c['id']+'-*'):shutil.copy2(old,archive/old.name)
   time.sleep(30)
   proc=subprocess.run(['pwsh','-NoProfile','-File',str(P/'chat-client/test-mcp-chat.ps1'),'-Question',c['question'],'-Model',pe.MODEL,'-McpEndpoint',pe.ENDPOINT,'-OutputDirectory',str(R/'chats'),'-OutputPrefix',c['id'],'-ToolProfile','full','-SaveTrace'],capture_output=True,text=True,encoding='utf-8',timeout=600)
   completed=f.exists() and pe.read(f).get('completed');event({'case':c['id'],'retry':attempt,'completed':completed,'exit_code':proc.returncode})
   if completed:break
elif phase=='paired-judge':
 for c in pe.read(R/'cases.json'):
  if c['id'] not in pe.CASE_IDS:continue
  for a in ['plain','mcp']:
   f=R/'paired-final'/(c['id']+'-'+a+'.json')
   if f.exists() and pe.read(f).get('completed'):continue
   for attempt in range(1,4):
    archive=R/'infrastructure-attempts'/'paired'/(c['id']+'-'+a+'-'+str(attempt)+'.json');archive.parent.mkdir(parents=True,exist_ok=True)
    if f.exists():shutil.copy2(f,archive)
    time.sleep(8)
    result=pe.answer(c,a);pe.save(f,result)
    event({'action':'retry_incomplete_pair','case':c['id'],'arm':a,'attempt':attempt,'completed':result['completed'],'prior_attempt_retained':str(archive.relative_to(R))})
    if result['completed']:break
   if not pe.read(f).get('completed'):raise RuntimeError('Incomplete paired answer remains; inspect before publishing')
 for c in pe.read(R/'cases.json'):
  if c['id'] not in pe.CASE_IDS:continue
  out=R/'paired-final';paired={a:pe.read(out/(c['id']+'-'+a+'.json')) for a in ['plain','mcp']};pool=pe.read(out/(c['id']+'-reference.json'))+paired['mcp'].get('calls',[])
  for a in ['plain','mcp']:
   f=out/(c['id']+'-'+a+'-judge.json')
   if f.exists():continue
   payload={'question':c['question'],'criteria':c['criteria'],'answer':paired[a]['answer'],'reference_evidence':pool}
   response=retry_model([{'role':'system','content':pe.JUDGE_PROMPT},{'role':'user','content':json.dumps(payload)}],judge=True)
   pe.save(f,{'judgment':json.loads(response['choices'][0]['message']['content']),'judge_model':pe.MODEL,'usage':response.get('usage'),'arm_label_hidden':True,'independent_clinician_review':False});event({'case':c['id'],'arm':a,'judged':True});time.sleep(8)
elif phase=='chat-judge':
 import score_current as sc
 sc.model_call=retry_model
 # Conserve the existing model service's rate allowance; rubric unchanged.
 source=(R/'score_current.py').read_text().replace('ThreadPoolExecutor(max_workers=2)','ThreadPoolExecutor(max_workers=1)').replace("if __name__=='__main__':main()",'')
 exec(compile(source,'serial-chat-judge','exec'),sc.__dict__);sc.model_call=retry_model;sc.main()
