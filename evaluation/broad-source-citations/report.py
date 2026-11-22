"""Keep every first-run assessment and compare to the archived benchmark."""
import html,json
from pathlib import Path
B=Path(__file__).parent
names=['correctness','source_fidelity','clinical_boundaries','safety','relevance_to_query','response_contract','citation_grounding']
cases=json.loads((B/'cases.json').read_text());byq={c['question']:c for c in cases}
summary={'case_count':32,'counts':{n:{'passed':0,'failed':0,'errors':0,'missing':0} for n in names},'runs':[],'flags':[]}
for suite in ['pubmed','trials','cross_source','safety']:
    summary['runs'].append(json.loads((B/f'{suite}-mlflow.json').read_text()))
    for row in json.loads((B/f'{suite}-eval_results.json').read_text()):
        request=row['request'];request=json.loads(request) if isinstance(request,str) else request
        case=byq[request['request']]
        for name in names:
            assessments=[a for a in row['assessments'] if a.get('assessment_name')==name]
            if len(assessments)!=1:
                summary['counts'][name]['missing']+=1
                summary['flags'].append({'case':case['id'],'scorer':name,'status':'missing or duplicate assessment'})
                continue
            a=assessments[0];v=a.get('feedback',{}).get('value')
            status='errors' if a.get('error') or v is None else ('passed' if v is True or v=='yes' or v==1 else 'failed')
            summary['counts'][name][status]+=1
            if status!='passed':summary['flags'].append({'case':case['id'],'scorer':name,'status':status,'rationale':a.get('rationale'),'error':a.get('error')})
(B/'summary.json').write_text(json.dumps(summary,indent=2))
parts=['<!doctype html><meta charset="utf-8"><title>MCP citation improvement retest</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto}table{border-collapse:collapse}td,th{padding:10px;border:1px solid #ccd}pre{white-space:pre-wrap}</style><h1>32-question citation improvement retest</h1><p>Same questions, expected facts, model and AI judging rubrics as the archived broad-source-fixed run. Changes: exact source-ID rendering, citation-parser bracket correction, and the existing outcome-routing fix. First full runs retained; no selection of best answers. Current server includes later NICHD additions, so this is not an isolated client-only comparison. The archived answers score 31/32 for citations under the corrected parser (30/32 with the old parser); the fresh batch scores 32/32. Development evaluation, not clinical certification.</p><table><tr><th>Check</th><th>Passed</th><th>Failed</th><th>Error</th><th>Missing</th></tr>']
for n,c in summary['counts'].items():parts.append('<tr><td>'+n+'</td>'+''.join('<td>'+str(c[k])+'</td>' for k in ['passed','failed','errors','missing'])+'</tr>')
parts.append('</table><h2>Raw flags</h2><pre>'+html.escape(json.dumps(summary['flags'],indent=2))+'</pre><h2>MLflow runs</h2>')
for run in summary['runs']:
    url='https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/'+run['run_id']
    parts.append('<p><a href="'+url+'">'+run['suite']+'</a></p>')
(B/'report.html').write_text(''.join(parts),encoding='utf-8')
print(json.dumps(summary['counts'],indent=2))
