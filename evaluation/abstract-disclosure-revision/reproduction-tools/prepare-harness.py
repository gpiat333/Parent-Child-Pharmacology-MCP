from pathlib import Path
import json
W=Path(__file__).parent;OLD=W.with_name('.submission-grader-attribution-review')
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/abstract-disclosure-revision'
def edit(name,fn):
 p=R/name;p.write_text(fn(p.read_text(encoding='utf-8')),encoding='utf-8')
def paired(s):
 s=s.replace('with or without deployed MCP tools','with or without local MCP tools').replace('Targets the existing updated Databricks app.','Targets the frozen local submission code; model calls use the existing Databricks gateway.')
 s=s.replace("ENDPOINT = 'https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp'","ENDPOINT = 'http://127.0.0.1:8770/mcp'")
 a=s.index("JUDGE_PROMPT = '''");b=s.index('\ndef save',a);s=s[:a]+'from grader_contract import JUDGE_PROMPT\n'+s[b:]
 s=s.replace("'max_tokens': 3000","'max_tokens': 6000 if judge else 3000")
 s=s.replace("format_required_notices(text,[c['tool'] for c in calls])", "format_required_notices(text,[c['tool'] for c in calls],tool_calls=calls)")
 s=s.replace("choices=['generate','judge']","choices=['generate']")
 a=s.index('\n    else:\n        for case in cases:',s.index('def main():'));b=s.index("\nif __name__",a)
 s=s[:a]+s[b:]
 s=s.replace('shared production instructions clarified for report context and neutral framing in both arms','shared updated application instructions in both arms')
 s=s.replace('appends applicable fixed application notices','appends applicable fixed and retrieval-coverage application notices')
 s=s.replace('Plain has no retrieval tools or application notices.','Plain has no retrieval tools or application notices. Fresh references and answers from local MCP .10; grader v3 unchanged.')
 return s
edit('paired_evaluation.py',paired)
edit('databricks_transport.py',lambda s:s.replace('Evaluation-only OAuth transport pinned to the existing Databricks MCP app.','Evaluation-only local transport and pinned existing Databricks authentication.').replace("    if endpoint!=ENDPOINT:","    if endpoint=='http://127.0.0.1:8770/mcp':\n        return httpx.Client(timeout=180,trust_env=False,follow_redirects=False,headers={'Accept':'application/json, text/event-stream'})\n    if endpoint!=ENDPOINT:"))
edit('run-chats.ps1',lambda s:s.replace('https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp','http://127.0.0.1:8770/mcp'))
edit('deployed_grader.py',lambda s:s.replace('Regrade frozen .9 responses with validated grader v3; no new answer generation.','Grade fresh local .10 captures with unchanged grader v3.').replace('Unchanged .9 response and reference pool; newly graded with v3.','Fresh local .10 response and reference pool; graded with unchanged v3.').replace("required_notices(names,d.get('policy_blocked',False))","required_notices(names,d.get('policy_blocked',False),tool_calls=calls)"))
edit('score_current.py',lambda s:s.replace('Regrading unchanged .9 answers and evidence.','Fresh local .10 answers and references.').replace('unchanged .9 captures regraded with grader v3','fresh local .10 captures graded with unchanged v3').replace('No new answer generation or source retrieval.','New answer generation and source retrieval; existing app not deployed.').replace(",'as_of':'2026-11-21 America/New_York'}","}"))
edit('mlflow_suite.py',lambda s:s.replace('mcp_replay_execution_20261121','mcp_abstract_local_execution_20261121').replace('mcp_diagnostic_v3_grounded_20261121','mcp_abstract_local_diagnostic_v3_20261121').replace('retained .9 deployed-app capture','fresh .10 local MCP capture'))
s=(OLD/'run-mlflow.py').read_text(encoding='utf-8').replace('evaluation/grader-attribution-revision','evaluation/abstract-disclosure-revision')
s=s.replace('mcp-mc-grader-v3-2026-11-21','mcp-mc-local-abstract-disclosure-2026-11-21').replace('local replay driver; grader model and MLflow in Databricks; .9 app unchanged','local .10 MCP and evaluation driver; model and MLflow in Databricks; deployed .9 app unchanged').replace("'policy_version':'2026-11-21.9'","'policy_version':'2026-11-21.10'")
s=s.replace("run_name='regraded-'","run_name='fresh-local-'").replace('unchanged .9 captures; precomputed replay evaluation','fresh local .10 captures; offline evaluation of saved answers').replace("'mcp_runtime':'Databricks Apps'","'mcp_runtime':'Local loopback submission .10; not deployed'").replace("'answer_generation_repeated':False","'answer_generation_repeated':True").replace("'pilot_rows_reused_in_full_run':args.phase in {'research','paired'}","'pilot_rows_reused_in_full_run':False")
(W/'run-mlflow.py').write_text(s,encoding='utf-8')
for name in ['verify-mlflow.py']:
 (W/name).write_text((OLD/name).read_text(encoding='utf-8').replace('evaluation/grader-attribution-revision','evaluation/abstract-disclosure-revision'),encoding='utf-8')
print('Fresh local answer generation and unchanged grader v3 prepared; no deployment path used.')
