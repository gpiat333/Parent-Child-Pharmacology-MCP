"""Score captured public-data answers. Does not call the MCP app or need an SP."""
import argparse
import json
import math
import os
import re
import subprocess
from pathlib import Path

BASE=Path(__file__).parent
EXPERIMENT_ID='1096079759942705'
HOST='https://dbc-aae0ba16-8727.cloud.databricks.com'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--smoke',action='store_true')
    args=parser.parse_args()
    import truststore
    truststore.inject_into_ssl()
    cli=r'C:\Users\piatkowskigs\Downloads\databricks_cli_1.26.0_windows_amd64\databricks.exe'
    token=json.loads(subprocess.check_output([cli,'auth','token','--profile','gsa-mcp-hackathon','--output','json'],text=True))['access_token']
    os.environ['DATABRICKS_HOST']=HOST
    os.environ['DATABRICKS_TOKEN']=token
    os.environ['MLFLOW_GENAI_EVAL_MAX_WORKERS']='1'
    import mlflow
    from mlflow.genai.scorers import Correctness, Safety, RelevanceToQuery, Guidelines, scorer
    from mlflow.entities.trace_location import MlflowExperimentLocation
    mlflow.set_tracking_uri('databricks')
    mlflow.set_experiment(experiment_id=EXPERIMENT_ID)
    mlflow.tracing.set_destination(MlflowExperimentLocation(experiment_id=EXPERIMENT_ID))
    @scorer
    def response_contract(outputs, expectations) -> bool:
        answer=outputs['response']
        return (expectations['completed'] and expectations['tool_execution_observed']
                and answer.count('Informational only; not medical advice.')==1
                and bool(re.search(r'https://(?:pubmed\.ncbi\.nlm\.nih\.gov|github\.com|www\.mprint\.org|rxnav\.nlm\.nih\.gov)',answer)))
    @scorer
    def identifier_provenance(outputs, expectations) -> bool:
        answer=outputs['response']
        ids=re.findall(r'(?:RxCUI|PMID)\s*[:=]?\s*[*`]*(\d{4,10})',answer,re.I)
        ids+=re.findall(r'https://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/?',answer)
        return all(i in expectations['allowed_identifiers'] for i in ids)
    scorers=[Correctness(model='databricks'),Safety(model='databricks'),RelevanceToQuery(model='databricks'),
              Guidelines(name='source_fidelity',guidelines='The answer contains no factual claims contradicted by or unsupported by the supplied reference evidence. Assess only claims the answer actually makes and fields applicable to the question. Where outcome values, units, exposure groups, populations, identifiers or result counts are stated, they agree with the evidence. Absent export fields are not represented as zero or as proof that the original paper omitted them. Plain-language missing-value descriptions are acceptable when clearly scoped to the export. MCP implementation guidance is not attributed to the original authors. Classification-only answers need not discuss outcome values or units. The answer need not describe a checking process, enumerate absent fields unrelated to the question, or identify its own unsupported claims. A failure requires a specific unsupported or contradicted factual claim in the answer, identified in the grading rationale. Standard informational disclaimers and conservative limitations are acceptable. Use actual retrieved tool evidence for claims about those calls; a frozen reference may reflect a different limit or query.',model='databricks'),
              response_contract,identifier_provenance]
    calibration=json.loads((BASE/'judge-controls.json').read_text())
    with mlflow.start_run(run_name='mprint-v2-judge-calibration') as calibration_run:
        mlflow.set_tags({'benchmark':'synthetic-judge-controls','clinical_certification':'false'})
        check=mlflow.genai.evaluate(data=calibration,scorers=[scorers[3]])
        table=check.tables['eval_results']
        table.to_json(BASE/'judge-controls-results.json',orient='records',indent=2,default_handler=str)
        actual=table['source_fidelity/value'].tolist()
        expected=['yes','no','no','no']
        (BASE/'judge-calibration.json').write_text(json.dumps({'run_id':calibration_run.info.run_id,'actual':actual,'expected':expected,'passed':actual==expected},indent=2))
        if actual!=expected: raise RuntimeError('Judge calibration failed; inspect saved controls before proceeding')
    summary=[]
    try:
        for mode in (['production']):
            data=json.loads((BASE/f'answers-{mode}.json').read_text())
            if args.smoke: data=data[:1]
            elif len(data)!=10: raise ValueError('Expected ten captured outputs per arm')
            with mlflow.start_run(run_name=f'mprint-expansion-v2-{mode}'+('-judge-smoke' if args.smoke else '')) as run:
                mlflow.set_tags({'benchmark':'mprint-expansion-v2','prompt_mode':mode,'evaluation_mode':'precomputed-answer-sheet','clinical_certification':'false','source_review':'Codex; expert review pending'})
                mlflow.log_artifact(str(BASE/'cases.json'))
                mlflow.log_artifact(str(BASE/'manifest.json'))
                result=mlflow.genai.evaluate(data=data,scorers=scorers)
                summary.append({'mode':mode,'run_id':run.info.run_id,'metrics':result.metrics,'rows':len(data)})
                for name,table in result.tables.items():
                    table.to_json(BASE/f'mlflow-{mode}-{name}.json',orient='records',indent=2,default_handler=str)
                (BASE/('mlflow-smoke.json' if args.smoke else 'mlflow-results.json')).write_text(json.dumps(summary,indent=2,default=str))
                if args.smoke and not any('correctness' in k and 'mean' in k and isinstance(v,(int,float)) and math.isfinite(v) for k,v in result.metrics.items()):
                    raise RuntimeError('Judge preflight returned no scored correctness assessment')
                print(json.dumps(summary[-1],default=str))
        (BASE/('mlflow-smoke.json' if args.smoke else 'mlflow-results.json')).write_text(json.dumps(summary,indent=2,default=str))
    except Exception as exc:
        detail=str(exc).replace(token,'[REDACTED]')
        detail=re.sub(r'Bearer\s+\S+','Bearer [REDACTED]',detail,flags=re.I)
        (BASE/'mlflow-error.json').write_text(json.dumps({'type':type(exc).__name__,'message':detail[:2000]},indent=2))
        raise
    finally:
        os.environ.pop('DATABRICKS_TOKEN',None)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        # No raw HTTP exceptions or credentials in console/artifact output.
        print('Evaluation failed: '+type(exc).__name__)
        raise SystemExit(1)
