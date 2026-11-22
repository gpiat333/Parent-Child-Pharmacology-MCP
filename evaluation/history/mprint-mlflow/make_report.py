import hashlib
import html
import json
from pathlib import Path

B = Path(__file__).parent
R = B.parent.parent
scores = json.loads((B / 'mlflow-results.json').read_text())[0]
rows = json.loads((B / 'mlflow-production-eval_results.json').read_text())
cases = json.loads((B / 'cases.json').read_text())
reviews = {
    'M01': 'Benchmark mismatch: the question asks for two studies but does not require max_results=2. The agent retrieved three records and described two; its returned count agrees with the actual tool response. The frozen key expected two returned. Keep the raw correctness failure; make the limit explicit in a future benchmark version.',
    'M02': 'Judge/rubric issue: the rationale requires outcome values and units in a classification comparison, and asks the answer itself to flag unsupported claims. It identifies no specific unsupported factual claim. Treat this flag as disputed, not an established server defect.',
    'M03': 'Wording improvement: null fields are rendered as "not reported". Prefer "missing in the exported data (null)" to avoid implying that the original paper did not report them. Numeric values and units otherwise match the retrieved rows. The judge demand for the literal word null is overly strict, but provenance wording can improve.',
    'M04': 'Judge/rubric issue: the rationale says the answer must explicitly perform the comparison and flag claims, instead of the judge checking its accuracy. It identifies no concrete incorrect value. Review confirms the requested third row and pagination. Attribute linkage caveats to this MCP implementation rather than implying they were written by the dataset authors.',
    'M10': 'Judge/rubric issue: a Silver classification-only question has no outcome values, units or missing-value comparison to report. The rationale identifies no concrete unsupported classification claim.',
}
names = ['correctness', 'source_fidelity', 'safety', 'relevance_to_query', 'response_contract', 'identifier_provenance']
feedback = [a for row in rows for a in row['assessments'] if a.get('assessment_name') in names]
errors = [a for a in feedback if a.get('error')]
assert len(feedback) == 60
assert not errors
result = {
    'mlflow': scores, 'unit_tests': {'passed': 87, 'failed': 0, 'elapsed_seconds': 8.24},
    'completed_chat_cases': 10, 'scorer_assessments': len(feedback), 'scorer_errors': len(errors),
    'review_type': 'AI-assisted source comparison; clinical expert review pending',
    'review_notes': reviews,
    'limitations': ['Development regression set, not held-out validation.',
        'Captured answers evaluated in MLflow; MCP tool calls retained locally, not instrumented as full MLflow tool spans.',
        'Safety is a general content-safety judge, not clinical safety or certification.',
        'Identifier provenance is a limited pattern/numeric-presence heuristic, not a complete semantic check.',
        'The custom source-fidelity rubric needs calibration: instructions to the judge were sometimes interpreted as answer requirements.',
        'No raw scores or frozen expected facts were changed after observing results. No deployment changes in this test run.']
}
(B / 'review-findings.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
files = [B/'cases.json', B/'assemble.py', B/'score_mlflow.py', R/'test-mcp-chat.ps1']
execution = {'deployment_revision': '01f1e2ceb2f91e24aa0d730f195b8f4b',
    'endpoint': 'https://mcp-mc-7474654188777746.aws.databricksapps.com/mcp',
    'model_alias': 'models.ai.gpt-5-6-luna', 'reasoning_effort': 'none', 'source_review_reasoning_effort': 'low',
    'file_sha256': {str(p.relative_to(R)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(B/'execution-manifest.json').write_text(json.dumps(execution, indent=2), encoding='utf-8')
link = 'https://dbc-aae0ba16-8727.cloud.databricks.com/ml/experiments/1096079759942705/runs/' + scores['run_id'] + '?o=7474654188777746'
parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>MPRINT evaluation</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px;color:#183041}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd6df;padding:10px;text-align:left}h1,h2{color:#285b79}li{margin:8px 0}pre{white-space:pre-wrap}</style>',
    '<h1>MPRINT expansion: live chat and MLflow evaluation</h1><p>November 17, 2026. 87 unit tests passed; 10 live chat cases completed; 60 scorer assessments; zero scorer errors.</p>',
    f'<p><a href="{link}">Open MLflow run {scores["run_id"]}</a></p><h2>Unmodified automated scores</h2><table><tr><th>Check</th><th>Passed / scored</th></tr>']
for name in names:
    parts.append(f'<tr><td>{name}</td><td>{round(scores["metrics"][name+"/mean"]*10)} / 10</td></tr>')
parts.append('</table><h2>Case results and review</h2>')
for case, row in zip(cases, rows):
    parts.append('<h3>'+case['id']+'</h3><p>'+html.escape(case['question'])+'</p>')
    flags = [a for a in row['assessments'] if a.get('feedback', {}).get('value') in [False, 'no']]
    for a in flags:
        parts.append('<p><b>Raw '+html.escape(a['assessment_name'])+' failure:</b> '+html.escape(a.get('rationale', ''))+'</p>')
    parts.append('<p><b>Review:</b> '+html.escape(reviews.get(case['id'], 'All six automated checks passed. No discrepancy identified in the saved-answer review.'))+'</p>')
    parts.append(f'<p><a href="../../presentation-evidence/mprint-eval-{case["id"]}-answer.txt">Saved answer</a> | <a href="../../presentation-evidence/mprint-eval-{case["id"]}-results.json">Tool evidence</a></p>')
parts.append('<h2>Limits and next steps</h2><ul>')
parts.extend('<li>'+html.escape(x)+'</li>' for x in result['limitations'])
parts.append('</ul><p>Next: clarify the count constraint in M01; calibrate the judge to evaluate only claims actually made and applicable fields; improve missing-data and implementation-caveat wording; then run a separately versioned evaluation. Expert clinical review remains outstanding.</p></html>')
(B/'report.html').write_text(''.join(parts), encoding='utf-8')
print(json.dumps({'report': str(B/'report.html'), 'assessments': len(feedback), 'errors': len(errors)}))
