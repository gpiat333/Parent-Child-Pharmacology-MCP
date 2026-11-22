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
    def gold_first_line(outputs, expectations) -> bool:
        text=outputs['response']
        first=next((s.strip() for s in text.splitlines() if s.strip()),'')
        first=re.sub(r'^answer\s*:\s*','',first.replace('*','').replace('`',''),flags=re.I).strip().rstrip('.').lower()
        return first in [a.lower() for a in expectations['accepted_answers']]
    scorers=[Correctness(model='databricks')]
    if not args.smoke:
        scorers += [Safety(model='databricks'),RelevanceToQuery(model='databricks'),Guidelines(name='conciseness',guidelines='The response states the requested value first and gives a brief relevant justification and source citation. Exactly one standard informational-only footer is allowed and is not verbosity. Source-specific limitations explicitly requested in the question must not be penalized as repetition. Repeating equivalent general disclaimers is unnecessary verbosity.',model='databricks'),gold_first_line]
    summary=[]
    try:
        for mode in (['production'] if args.smoke else ['production']):
            data=json.loads((BASE/f'answers-{mode}.json').read_text())
            if args.smoke: data=data[:1]
            elif len(data)!=10: raise ValueError('Expected ten captured outputs per arm')
            with mlflow.start_run(run_name=f'gold-v2-{mode}'+('-judge-smoke' if args.smoke else '')) as run:
                mlflow.set_tags({'benchmark':'mother-child-gold-v2','prompt_mode':mode,'evaluation_mode':'precomputed-answer-sheet','clinical_certification':'false','source_review':'Codex; expert review pending'})
                mlflow.log_artifact(str(BASE/'gold-questions.json'))
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
