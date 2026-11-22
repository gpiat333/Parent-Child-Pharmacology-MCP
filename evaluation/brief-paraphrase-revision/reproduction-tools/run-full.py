from pathlib import Path
import json, os, subprocess, sys
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/brief-paraphrase-revision'
os.chdir(W)
assert json.loads((R/'mlflow/pilot-verification.json').read_text())['all_applicable_scores_present']
target=R/'routing-regression/give-results.json'
if not target.exists():
 print('End-to-end paraphrase regression',flush=True)
 result=subprocess.run(['pwsh','-NoProfile','-File',str(P/'chat-client/test-mcp-chat.ps1'),'-Question','Give me a pregnancy evidence brief for lamotrigine.','-Model','system.ai.gpt-5-6-luna','-McpEndpoint','https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp','-OutputDirectory',str(target.parent),'-OutputPrefix','give','-ToolProfile','full','-SaveTrace'],capture_output=True,text=True,encoding='utf-8')
 (R/'routing-regression/client.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
 assert result.returncode==0,'Inspect regression capture before retrying'
d=json.loads(target.read_text(encoding='utf-8-sig'))
assert d['completed'] and d['requested_workflow']['required_tool']=='medication_evidence_brief'
assert d['tool_calls'][0]['tool']=='medication_evidence_brief'
(R/'routing-regression/verification.json').write_text(json.dumps({'question':d['question'],'completed':d['completed'],'first_evidence_tool':d['tool_calls'][0]['tool'],'required_workflow':d['requested_workflow'],'excluded_from_28_case_benchmark':True,'not_clinical_validation':True},indent=2),encoding='utf-8')
for command in [
 ['run-chat-suite.py'],['verify-mlflow.py','research'],['verify-mlflow.py','stops'],
 ['run-paired-suite.py'],['verify-mlflow.py','paired']
]:
 print('Full evaluation stage: '+command[0]+' '+' '.join(command[1:]),flush=True)
 subprocess.run([sys.executable,'-X','utf8',str(W/command[0]),*command[1:]],cwd=W,check=True)
print('All captures and MLflow row readbacks completed.',flush=True)
