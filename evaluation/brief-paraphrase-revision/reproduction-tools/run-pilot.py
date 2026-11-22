from pathlib import Path
import json, subprocess, sys, os
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/brief-paraphrase-revision'
cases=json.loads((R/'cases.json').read_text(encoding='utf-8'))
os.chdir(W)
for case in cases:
 if case['id'] not in ['P01-portfolio','S6-pregnancy','R12']:continue
 target=R/'chats'/(case['id']+'-results.json')
 if target.exists():
  assert json.loads(target.read_text(encoding='utf-8-sig'))['completed'];continue
 print('Capturing pilot '+case['id'],flush=True)
 result=subprocess.run(['pwsh','-NoProfile','-File',str(P/'chat-client/test-mcp-chat.ps1'),'-Question',case['question'],'-Model','system.ai.gpt-5-6-luna','-McpEndpoint','https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp','-OutputDirectory',str(R/'chats'),'-OutputPrefix',case['id'],'-ToolProfile','full','-SaveTrace'],capture_output=True,text=True,encoding='utf-8')
 (R/(case['id']+'-pilot-client.log')).write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
 assert result.returncode==0,case['id']
 assert json.loads(target.read_text(encoding='utf-8-sig'))['completed'],case['id']
 print('Completed '+case['id'],flush=True)
subprocess.run([sys.executable,'-X','utf8',str(W/'run-mlflow.py'),'--phase','pilot'],check=True,cwd=W)
subprocess.run([sys.executable,'-X','utf8',str(W/'verify-mlflow.py'),'pilot'],check=True,cwd=W)
