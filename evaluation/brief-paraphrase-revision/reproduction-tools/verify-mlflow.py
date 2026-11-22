from pathlib import Path
import sys,os,json,subprocess
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/brief-paraphrase-revision');phase=sys.argv[1]
if '--child' not in sys.argv:
    try:
        result=subprocess.run([sys.executable,'-X','utf8',str(Path(__file__)),phase,'--child'],timeout=55,capture_output=True,text=True,encoding='utf-8',cwd=W)
        print(result.stdout)
        if result.returncode:print(result.stderr[-2200:])
        raise SystemExit(result.returncode)
    except subprocess.TimeoutExpired:
        print('Readback exceeded the 55-second process deadline.');raise SystemExit(2)
os.chdir(W);sys.path.insert(0,str(Path(r'C:/Users/piatkowskigs/Desktop/.submission-databricks-review/python-deps')));sys.path.insert(0,str(R))
os.environ.update(MLFLOW_DISABLE_AGENT_HINT='1',MLFLOW_HTTP_REQUEST_TIMEOUT='10',MLFLOW_HTTP_REQUEST_MAX_RETRIES='0')
from databricks_transport import HOST,CLI
import truststore;truststore.inject_into_ssl()
os.environ.pop('DATABRICKS_TOKEN',None)
os.environ.update(DATABRICKS_HOST=HOST,DATABRICKS_CONFIG_PROFILE='gsa-mcp-hackathon',DATABRICKS_AUTH_TYPE='databricks-cli',DATABRICKS_CLI_PATH=CLI,MLFLOW_ENABLE_DB_SDK='true')
import mlflow
mlflow.set_tracking_uri('databricks://gsa-mcp-hackathon');client=mlflow.MlflowClient()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
summary=read(R/'mlflow'/(phase+'-run.json'));rows=read(R/'mlflow'/(phase+'-eval_results.json'))
run=client.get_run(summary['run_id']);assert run.info.status=='FINISHED',run.info.status
traces=mlflow.search_traces(run_id=summary['run_id'],locations=[summary['experiment_id']],filter_string='trace.timestamp_ms >= '+str(run.info.start_time-60000),max_results=50,include_spans=False,return_type='list')
byid={t.info.trace_id:t for t in traces};assert set(byid)=={r['trace_id'] for r in rows},(len(byid),len(rows))
verified=[]
for row in rows:
    trace=byid[row['trace_id']];values={a.name:a.value for a in trace.info.assessments if hasattr(a,'value')}
    errors=[a.name for a in trace.info.assessments if getattr(a,'error',None)];assert not errors,errors
    expected={k[:-6]:v for k,v in row.items() if k.endswith('/value') and isinstance(v,bool)}
    assert expected and all(values.get(k)==v and isinstance(values.get(k),bool) for k,v in expected.items()),(row['trace_id'],expected,values)
    if phase=='paired':assert 'diagnostic_task_fulfilled' in expected and 'fidelity_assessable' in expected
    elif phase=='stops':assert all(k in expected for k in ['completed','expected_route','required_allowed_tools','fixed_stop_no_downstream_calls'])
    else:assert all(k in expected for k in ['completed','expected_route','required_allowed_tools','url_membership','diagnostic_task_fulfilled','fidelity_assessable'])
    verified.append({'trace_id':row['trace_id'],'scores':expected})
artifact_path='paired-final' if phase=='paired' else 'chats';arts=client.list_artifacts(summary['run_id'],artifact_path)
capture_count=sum(a.path.endswith(('-mcp.json','-plain.json')) for a in arts) if phase=='paired' else len(arts)
assert capture_count==len(rows),(capture_count,len(rows))
out={'phase':phase,'run_id':summary['run_id'],'status':run.info.status,'rows_verified':len(rows),'all_applicable_scores_present':True,'assessment_errors':0,'raw_capture_artifacts_verified':capture_count,'not_assessable_count':sum(t['scores'].get('fidelity_assessable') is False for t in verified),'false_scores_retained':sum(v is False for t in verified for v in t['scores'].values()),'traces':verified}
(R/'mlflow'/(phase+'-verification.json')).write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='traces'},indent=2))
