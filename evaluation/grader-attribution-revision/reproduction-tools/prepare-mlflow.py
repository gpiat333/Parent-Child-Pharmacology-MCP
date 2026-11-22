from pathlib import Path
import hashlib,json
W=Path(__file__).parent;W9=W.parent/'.submission-report-context-review'
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/grader-attribution-revision'
source=(W9/'run-mlflow.py').read_text(encoding='utf-8')
source=source.replace('report-context-revision','grader-attribution-revision')
source=source.replace("R/'app-after.json'","R/'app-current.json'")
source=source.replace("'mcp-mc-deployed-2026-11-21.9'","'mcp-mc-grader-v3-2026-11-21'")
source=source.replace("'local; deployed app/model/tracking in Databricks'","'local replay driver; grader model and MLflow in Databricks; .9 app unchanged'")
source=source.replace("'policy_version':'2026-11-21.9'","'policy_version':'2026-11-21.9','grader_version':'3.0'")
source=source.replace("run_name='deployed-'+label+'-2026-11-21.9'","run_name='regraded-'+label+'-v3-2026-11-21'")
source=source.replace("'input_mode':'fresh deployed captures; precomputed MLflow evaluation'","'input_mode':'unchanged .9 captures; precomputed replay evaluation'")
source=source.replace("'grader':'unchanged-v2'","'grader':'v3-grounded-attribution'")
source=source.replace("'pilot_rows_reused_in_full_run':args.phase=='research'","'pilot_rows_reused_in_full_run':args.phase in {'research','paired'},'answer_generation_repeated':False")
source=source.replace("R/'deployment-source-manifest.json'","R/'capture-lineage.json'")
source=source.replace("R/'deployed_grader.py',R/'mlflow_suite.py',summary_path","R/'deployed_grader.py',R/'mlflow_suite.py',R/'grader_contract.py',R/'grader_runtime.py',summary_path")
(W/'run-mlflow.py').write_text(source,encoding='utf-8')
verify=(W9/'verify-mlflow.py').read_text(encoding='utf-8').replace('report-context-revision','grader-attribution-revision')
(W/'verify-mlflow.py').write_text(verify,encoding='utf-8')
suite=(R/'mlflow_suite.py').read_text(encoding='utf-8')
suite=suite.replace("feedback=[Feedback(name='diagnostic_task_fulfilled'","feedback=[Feedback(name='grade_attribution_valid',value=record['grounding_validated'],rationale='Structured negative claims use validated candidate quotes; omissions are anchored to requested requirements. This is not semantic or clinical validation.'),\n              Feedback(name='diagnostic_task_fulfilled'")
(R/'mlflow_suite.py').write_text(suite,encoding='utf-8')
print('Prepared new v3 MLflow scorer; v2 registered scorer and historical runs remain unchanged.')
