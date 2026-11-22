from pathlib import Path
from datetime import datetime,timezone
import json,subprocess
import os,shutil
R=Path(__file__).parent;O=R/'inspector';O.mkdir(exist_ok=True)
NODE=os.environ.get('NODE_PATH_EXECUTABLE',shutil.which('node'))
CLI=Path(os.environ['MCP_INSPECTOR_CLI'])
ENDPOINT=os.environ['MCP_EVAL_ENDPOINT'];checks=[];results={}

def invoke(name,method,args,check):
 command=[NODE,str(CLI),'--cli',ENDPOINT,'--transport','http','--method',method,*args]
 r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=100)
 (O/(name+'-stdout.txt')).write_text(r.stdout,encoding='utf-8');(O/(name+'-stderr.txt')).write_text(r.stderr,encoding='utf-8')
 value=json.loads(r.stdout[r.stdout.index('{'):]);(O/(name+'.json')).write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
 passed=bool(check(value));checks.append({'name':name,'method':method,'arguments':args,'exit_code':r.returncode,'passed':passed});results[name]=value
 assert passed,(name,r.returncode,r.stderr[-500:]);print(name,'passed',flush=True)
def unpack(v):return v.get('structuredContent') or json.loads(v['content'][0]['text'])
invoke('tools','tools/list',[],lambda v:len(v['tools'])==30 and all(t.get('inputSchema',{}).get('type')=='object' for t in v['tools']))
invoke('resources','resources/list',[],lambda v:len(v['resources'])==4)
invoke('prompts','prompts/list',[],lambda v:len(v['prompts'])==4)
invoke('disclaimer','resources/read',['--uri','parent-child://disclaimer'],lambda v:bool(v['contents']))
invoke('research-route','tools/call',['--tool-name','route_parent_question','--tool-arg','question=What evidence exists for sertraline during breastfeeding? Do not provide medication decisions or doses.'],lambda v:unpack(v)['allow_research'] is True)
invoke('identity-stop','tools/call',['--tool-name','route_parent_question','--tool-arg','question=What is my little white pill?'],lambda v:unpack(v)['allow_research'] is False)
invoke('crisis-stop','tools/call',['--tool-name','route_parent_question','--tool-arg','question=I feel hopeless since giving birth. Can you tell me about sertraline?'],lambda v:unpack(v)['allow_research'] is False and unpack(v)['allow_model_answer'] is False and unpack(v)['route']=='mental_health_support')
invoke('missing-abstract','tools/call',['--tool-name','get_abstracts','--tool-arg','pmids=["36630579","35802843","36630580"]'],lambda v:unpack(v)['abstract_coverage']['without_abstract_pmids']==['36630579','35802843','36630580'] and any(n['id']=='pubmed_abstract_coverage' for n in unpack(v)['required_display_notices']))
invoke('negative-bound','tools/call',['--tool-name','search_literature','--tool-arg','query=amoxicillin','--tool-arg','max_results=-1'],lambda v:v.get('isError') is True)
summary={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'inspector_version':'1.0.6','mode':'Official MCP Inspector CLI, security-maintained v1 release','endpoint':ENDPOINT,'checks':len(checks),'passed':sum(c['passed'] for c in checks),'inventory':{'tools':30,'prompts':4,'resources':4},'results':checks,'limits':'Protocol, schema and explicit tool contracts only; no clinical validation. No remote deployment or credentials supplied to Inspector.'}
(O/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='results'},indent=2))
