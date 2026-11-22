"""Registered offline scorer adapters; no continuous monitoring is enabled."""
from mlflow.genai.scorers import scorer

@scorer(name='mcp_deployed_execution_20261121')
def execution_contracts(inputs,outputs,expectations):
    from mlflow.entities import Feedback
    from deployed_grader import execution
    return [Feedback(name=name,value=value,rationale='Deterministic contract check on a fresh deployed-app capture; not clinical validation.') for name,value in execution(inputs,outputs,expectations).items()]

@scorer(name='mcp_diagnostic_v2_20261121')
def diagnostic_contracts(inputs,outputs,expectations):
    from mlflow.entities import Feedback
    from deployed_grader import diagnostic
    record=diagnostic(inputs,outputs,expectations);j=record['judgment']
    feedback=[Feedback(name='diagnostic_task_fulfilled',value=j['task_fulfilled'],rationale=j['rationale']),
              Feedback(name='fidelity_assessable',value=j['fidelity_status']!='not_assessable',rationale='False means no assessable factual source claim; it is excluded from fidelity-pass aggregation.')]
    if j['fidelity_status']!='not_assessable':feedback.append(Feedback(name='diagnostic_fidelity_pass',value=j['fidelity_status']=='pass',rationale=j['rationale']))
    return feedback
