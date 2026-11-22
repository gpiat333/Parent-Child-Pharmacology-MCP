from pathlib import Path
import sys,os,json
W=Path(__file__).parent;R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/databricks-validation-2026-11-21')
os.chdir(W);sys.path.insert(0,str(W/'python-deps'));sys.path.insert(0,str(R))
import truststore;truststore.inject_into_ssl()
from databricks_transport import HOST,CLI
os.environ.pop('DATABRICKS_TOKEN',None)
os.environ.update(DATABRICKS_HOST=HOST,DATABRICKS_CONFIG_PROFILE='gsa-mcp-hackathon',DATABRICKS_AUTH_TYPE='databricks-cli',DATABRICKS_CLI_PATH=CLI,MLFLOW_ENABLE_DB_SDK='true',MLFLOW_HTTP_REQUEST_TIMEOUT='10',MLFLOW_HTTP_REQUEST_MAX_RETRIES='0',MLFLOW_DISABLE_AGENT_HINT='1')
import mlflow
mlflow.set_tracking_uri('databricks://gsa-mcp-hackathon');c=mlflow.MlflowClient();rows=[]
for p in sorted((R/'mlflow').glob('*-run.json')):
    d=json.loads(p.read_text());run=c.get_run(d['run_id']);wrong={k:v for k,v in run.data.tags.items() if k.startswith('mlflow.source.git.')}
    if wrong:
        for k in wrong:c.delete_tag(d['run_id'],k)
    c.set_tag(d['run_id'],'evaluated_project','Parent-child Pharmacology MCP (Mother-child MCP)')
    c.set_tag(d['run_id'],'source_of_truth','Submission folder; local-source-freeze.json and deployed-source-verification.json; no GitHub repository assigned')
    c.set_tag(d['run_id'],'source_context_note','Early process inherited NIHRePORTERAgent working directory; any automatic Git metadata from that directory is unrelated to evaluated source. Source hashes identify the MCP build.')
    tables=list((R/'mlflow').glob(p.name.replace('-run.json','-eval_results.json')))
    n=0
    for table in tables:
        for row in json.loads(table.read_text()):
            c.set_trace_tag(row['trace_id'],'source_context','Parent-child Pharmacology MCP submission; verify source hashes. Automatic Git metadata from NIHRePORTERAgent cwd is unrelated. No GitHub upload.')
            n+=1
    rows.append({'run_id':d['run_id'],'removed_unrelated_run_tags':wrong,'trace_source_annotations':n})
out={'reason':'MLflow inferred the chat working directory as Git source; actual evaluated code came from the separately frozen submission folder. Corrected run tags and annotated existing trace metadata; raw answers, scores and original local result tables retained. Future processes start outside the unrelated Git repository.','rows':rows}
(R/'mlflow/source-context-correction.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'runs_annotated':len(rows),'traces_annotated':sum(r['trace_source_annotations'] for r in rows)}))
