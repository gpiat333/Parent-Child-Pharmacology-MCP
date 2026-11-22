from pathlib import Path
from datetime import datetime,timezone
import os,sys,json
W=Path(__file__).parent;P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/grader-attribution-revision'
os.chdir(W);sys.path.insert(0,str(W.parent/'.submission-databricks-review/python-deps'));sys.path.insert(0,str(R))
import truststore;truststore.inject_into_ssl()
from databricks_transport import HOST,CLI
os.environ.pop('DATABRICKS_TOKEN',None)
os.environ.update(DATABRICKS_HOST=HOST,DATABRICKS_CONFIG_PROFILE='gsa-mcp-hackathon',DATABRICKS_AUTH_TYPE='databricks-cli',DATABRICKS_CLI_PATH=CLI,MLFLOW_ENABLE_DB_SDK='true',MLFLOW_HTTP_REQUEST_TIMEOUT='30',MLFLOW_HTTP_REQUEST_MAX_RETRIES='1',MLFLOW_DISABLE_AGENT_HINT='1')
import mlflow
mlflow.set_tracking_uri('databricks://gsa-mcp-hackathon');c=mlflow.MlflowClient()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
S=read(R/'summary.json');parent=S['mlflow']['parent']['run_id']
assert read(R/'final-validation.json')['mlflow_final_rows_verified']==42
for phase in ['research','stops','paired']:
 v=read(R/'mlflow'/(phase+'-verification.json'));assert v['assessment_errors']==0 and c.get_run(v['run_id']).info.status=='FINISHED'
 c.set_tag(v['run_id'],'evaluated_project','Parent-child Pharmacology MCP (Mother-child MCP)')
 c.set_tag(v['run_id'],'answer_generation_repeated','false')
metrics={'fresh_server_tests':562,'grader_tests':30,'synthetic_control_matches':10,'retained_chats':28,'retained_route_pass':S['chat']['counts']['boundary_behavior']['passed']/28,'retained_tool_pass':S['chat']['counts']['tool_selection']['passed']/28,'research_fidelity_pass_count':S['chat']['diagnostic_grading']['fidelity_pass'],'research_task_pass_count':S['chat']['diagnostic_grading']['task_fulfilled'],'mcp_paired_task_count':S['paired']['mcp']['task_fulfilled'],'plain_paired_task_count':S['paired']['plain']['task_fulfilled'],'mlflow_final_rows_verified':42,'assessment_errors':0,'answer_generation_calls':0,'app_deployments_this_revision':0}
for k,v in metrics.items():c.log_metric(parent,k,v)
for name in ['REPORT.md','summary.json','TECHNICAL_REVIEW.md','grading-review.json','grading-deltas.json','final-validation.json','local-source-freeze.json','local-unit-tests.xml','grader-unit-tests.xml','run-design.json','run-design-verification.json','capture-lineage.json','artifact-review.json','presentation-validation.json','grader-changes.diff','grader-changes.json','calibration.json','calibration-summary.json','chat-summary.json','chat-checks.json','paired-summary.json','artifact-metric-consistency.json','pilot-verification.json']:
 c.log_artifact(parent,str(R/name),'summary')
for f in sorted((R/'mlflow').glob('*verification.json')):c.log_artifact(parent,str(f),'readbacks')
for folder in ['chat-judge-inputs','paired-judge-inputs','development']:
 c.log_artifacts(parent,str(R/folder),folder)
for f in [P/'presentation/Parent-child Pharmacology MCP — Updated.pptx',P/'documentation/Parent-child Pharmacology MCP - Evaluation.docx']:c.log_artifact(parent,str(f),'submission-artifacts')
c.log_artifact(parent,str(R/'evaluation-harness.zip'),'reproduction-tools')
for k,v in {'source_verified':'114 unchanged application files; 77 identical retained capture files','evaluation_completion':'42 replay rows verified; no new answers or retrieval','clinical_validation':'false','github_push':'false','app_deployment':'false','manual_score_overrides':'false'}.items():c.set_tag(parent,k,v)
c.set_terminated(parent,status='FINISHED')
run=c.get_run(parent);assert run.info.status=='FINISHED'
arts=c.list_artifacts(parent,'submission-artifacts');assert len(arts)==2
out={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'run_id':parent,'status':run.info.status,'url':S['mlflow']['parent']['url'],'submission_artifacts':[{'path':a.path,'file_size':a.file_size} for a in arts],'final_rows_verified':42,'historical_scores_changed':False,'manual_overrides':False,'app_deployment':False,'github_push':False}
(R/'mlflow/parent-final-state.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
