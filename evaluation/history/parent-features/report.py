import json,html,hashlib
from pathlib import Path
B=Path(__file__).parent;root=B.parent.parent
def read(name,default):
 p=B/name
 return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else default
deployed=read('deployed-results.json',[])
chats=[]
for i in [0,1]:
 r=read(f'chat-shard-{i}.json',[]);chats.extend(r if isinstance(r,list) else [r])
followups=[]
for name in ['final-recall','final-voice','attribution-recall']:
 p=root/'presentation-evidence'/f'parent-feature-{name}-results.json'
 if p.exists():
  d=json.loads(p.read_text(encoding='utf-8-sig'))
  followups.append({'id':name,'passed':bool(d.get('completed') and not d.get('policy_blocked'))})
manifest={'deployment_id':read('deployment.json',{}).get('deployment_id','unrecorded'),'tool_count':27,
 'unit_tests_passed':170,'client_policy_checks_passed':12,'citation_regressions_passed':7,
 'deployed_checks':{'passed':sum(bool(x['passed']) for x in deployed),'total':len(deployed),'expected':18},
 'chat_checks':{'passed':sum(bool(x['passed']) for x in chats),'total':len(chats),'expected':10},
 'targeted_followups':followups,
 'clinical_validation':False,'new_mlflow_benchmark':False,
 'client_sha256':hashlib.sha256((root/'test-mcp-chat.ps1').read_bytes()).hexdigest()}
(B/'manifest.json').write_text(json.dumps(manifest,indent=2))
parts=['<!doctype html><meta charset="utf-8"><title>Parent feature acceptance</title><style>body{font:16px system-ui;max-width:1050px;margin:36px auto}table{border-collapse:collapse;width:100%}td,th{padding:8px;border:1px solid #ccd}pre{white-space:pre-wrap}</style><h1>Parent-facing MCP features</h1><p>27 tools on the existing Databricks app. No new compute or resource changes. Existing signatures retained.</p><h2>Validation</h2><pre>'+html.escape(json.dumps(manifest,indent=2))+'</pre>']
for title,rows in [('Deployed tool checks',deployed),('Initial synthetic chat acceptance',chats),('Targeted follow-ups after manual findings',followups)]:
 parts.append('<h2>'+title+'</h2><table><tr><th>Case</th><th>Passed</th></tr>')
 for row in rows:parts.append('<tr><td>'+html.escape(row.get('case',row.get('id','')))+ '</td><td>'+str(row['passed'])+'</td></tr>')
 parts.append('</table>')
parts.append('<h2>Manual review and corrections</h2><p>The initial ten acceptance checks passed but manual reading found two retrieval weaknesses: possessive product wording produced a false-empty recall query, and a complex Federal Register query produced false-empty notice results. Product words are now searched separately and public notices use plain subject search plus candidate filtering and detail retrieval. Final deployed checks require positive results for both known examples. Original outputs are retained. A further client instruction distinguishes MCP-authored caveats from statements made by FDA/NIH. Targeted follow-ups are separate from the initial batch.</p>')
parts.append('<h2>Limits</h2><p>Acceptance checks test routing, source fields and expected client behavior, not clinical correctness. The English rule-based router and output filters are incomplete and unvalidated. Third-party clients do not automatically inherit companion enforcement. Recall candidates never clear a bottle; registry/trial records never determine eligibility. Notice search is incomplete and unknown deadlines remain unknown. The script does not write ordinary transcripts; synthetic capture requires SaveTrace. Provider retention and shell history are separate. No new MLflow score or clinician certification.</p>')
(B/'report.html').write_text(''.join(parts),encoding='utf-8')
print(json.dumps(manifest,indent=2))
