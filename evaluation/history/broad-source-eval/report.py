import html,json
from pathlib import Path
B=Path(__file__).parent;R=B.parent.parent
suites=['pubmed','trials','cross_source','safety']
names=['correctness','source_fidelity','clinical_boundaries','safety','relevance_to_query','response_contract','citation_grounding']
cases=json.loads((B/'cases.json').read_text());by_question={c['question']:c for c in cases}
summary={'case_count':32,'runs':[],'assessment_count':0,'scorer_errors':0,'flags':[]}
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Broad MCP evaluation</title><style>body{font:15px system-ui;max-width:1200px;margin:32px auto;padding:20px;color:#183041}table{border-collapse:collapse;width:100%;margin:18px 0}td,th{border:1px solid #ccd6df;padding:9px;text-align:left;vertical-align:top}h1,h2{color:#285b79}li{margin:8px 0}details{margin:14px 0}summary{cursor:pointer}code{overflow-wrap:anywhere}</style><h1>Broad MCP evaluation: 32 new questions</h1><p>November 17, 2026. Four MLflow evaluation runs in the existing Databricks experiment. Questions and source-backed expectations were frozen before the chat runs. Production server and client were not modified during this batch.</p>']
for suite in suites:
 score=json.loads((B/f'{suite}-mlflow.json').read_text())
 rows=json.loads((B/f'{suite}-eval_results.json').read_text())
 execution=json.loads((B/f'{suite}-execution.json').read_text())
 counts={n:{'passed':0,'failed':0,'errors':0,'missing':0} for n in names}
 per_case=[]
 for row in rows:
  request=row['request'];request=json.loads(request) if isinstance(request,str) else request
  case=by_question[request['request']]
  verdicts={};flags=[]
  for n in names:
   found=[a for a in row['assessments'] if a.get('assessment_name')==n]
   if not found:counts[n]['missing']+=1;verdicts[n]='missing';continue
   for a in found:
    summary['assessment_count']+=1
    val=a.get('feedback',{}).get('value')
    if a.get('error') or val is None:
     counts[n]['errors']+=1;summary['scorer_errors']+=1;verdict='error'
    elif val is True or val=='yes' or val==1:
     counts[n]['passed']+=1;verdict='pass'
    else:counts[n]['failed']+=1;verdict='fail'
    verdicts[n]=verdict
    if verdict!='pass':
     flag={'id':case['id'],'suite':suite,'scorer':n,'verdict':verdict,'rationale':a.get('rationale'),'error':a.get('error') or a.get('feedback',{}).get('error')}
     flags.append(flag);summary['flags'].append(flag)
  per_case.append({'id':case['id'],'question':case['question'],'verdicts':verdicts,'flags':flags})
 url='https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/'+score['run_id']+'?o=7474654188777746'
 run={**score,'url':url,'counts':counts,'completed_chats':sum(x['completed'] for x in execution),'case_results':per_case}
 summary['runs'].append(run)
 parts.append(f'<h2>{html.escape(suite.replace("_"," ").title())}</h2><p><a href="{url}">MLflow run {score["run_id"]}</a>. {run["completed_chats"]}/8 chat answers completed.</p><table><tr><th>Check</th><th>Pass</th><th>Fail</th><th>Error / missing</th></tr>')
 for n,c in counts.items():parts.append(f'<tr><td>{n}</td><td>{c["passed"]}</td><td>{c["failed"]}</td><td>{c["errors"]} / {c["missing"]}</td></tr>')
 parts.append('</table>')
 for c in per_case:
  parts.append('<details><summary>'+c['id']+' — '+html.escape(c['question'])+'</summary><p>'+html.escape(str(c['verdicts']))+'</p>')
  for flag in c['flags']:parts.append('<p><b>'+flag['scorer']+':</b> '+html.escape(str(flag['rationale'] or flag['error']))+'</p>')
  parts.append(f'<p><a href="../../presentation-evidence/broad-v1-{c["id"]}-answer.txt">Saved answer</a> · <a href="../../presentation-evidence/broad-v1-{c["id"]}-results.json">Tool trace</a></p></details>')
review_path=B/'review-notes.json'
if review_path.exists():
 review=json.loads(review_path.read_text());summary['manual_review']=review
 parts.append('<h2>Review notes</h2><ul>')
 for note in review:parts.append('<li>'+html.escape(note)+'</li>')
 parts.append('</ul>')
retry_path=B/'judge-retries.json'
if retry_path.exists():
 retries=json.loads(retry_path.read_text());summary['judge_error_retries']=retries
 parts.append('<h2>Separate retry of judge execution errors</h2><p>Original runs and negative verdicts were not changed. Only failed scorer executions were retried with the same answer and rubric.</p><ul>')
 for retry in retries:
  url='https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/'+retry['run_id']+'?o=7474654188777746'
  parts.append('<li>'+html.escape(retry['suite']+' / '+retry['scorer'])+f': <a href="{url}">retry run</a>; metrics '+html.escape(str(retry['metrics']))+'</li>')
 parts.append('</ul>')
parts.append('<h2>Method and limits</h2><ul><li>Seven checks per answer: correctness, source fidelity, clinical boundaries, general content safety, relevance, response/tool requirements, and citation grounding. Citations are checked against returned URLs; canonical PubMed links are allowed for retrieved PMIDs.</li><li>Expected facts were prepared from source snapshots by Codex, not independently approved by a clinician. This is a development evaluation, not clinical certification or a guarantee of future answers.</li><li>The clinical-boundaries judge is an LLM rubric, not a medical-certification process. General Safety checks prohibited content rather than comprehensive clinical safety.</li><li>Frozen references and actual retrieved tool results are supplied to the judges. Current tool evidence takes precedence for genuinely changing live fields. Judges can miss errors or produce false flags, so raw scores and manual review are both retained.</li><li>Trials include completed, active-not-recruiting, unknown, not-yet-recruiting and withdrawn statuses. This suite does not cover every recruitment status or every medical population.</li><li>No cases were discarded because they failed; no answer keys were revised after seeing answers. Two strict automated code checks assess required tools and cited URL provenance, not all aspects of reasoning quality.</li><li>Chat execution artifacts contain source calls; MLflow evaluates captured answers rather than a fully instrumented end-to-end tool trace.</li></ul></html>')
(B/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
(B/'report.html').write_text(''.join(parts),encoding='utf-8')
assert summary['assessment_count']==224
assert sum(r['completed_chats'] for r in summary['runs'])==32
print(json.dumps({'assessments':summary['assessment_count'],'original_errors':summary['scorer_errors'],'judge_error_retries':len(summary.get('judge_error_retries',[])),'correctness':{r['suite']:r['counts']['correctness'] for r in summary['runs']},'report':str(B/'report.html')},ensure_ascii=True))
