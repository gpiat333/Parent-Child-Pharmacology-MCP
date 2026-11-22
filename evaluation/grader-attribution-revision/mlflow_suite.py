"""Registered offline scorer adapters; no continuous monitoring is enabled."""
from mlflow.genai.scorers import scorer

@scorer(name='mcp_replay_execution_20261121')
def execution_contracts(inputs,outputs,expectations):
    from mlflow.entities import Feedback
    from deployed_grader import execution
    return [Feedback(name=name,value=value,rationale='Deterministic contract check on a retained .9 deployed-app capture; not clinical validation.') for name,value in execution(inputs,outputs,expectations).items()]

@scorer(name='mcp_diagnostic_v3_grounded_20261121')
def diagnostic_contracts(inputs,outputs,expectations):
    from mlflow.entities import Feedback
    from deployed_grader import diagnostic
    record=diagnostic(inputs,outputs,expectations);j=record['judgment']
    feedback=[Feedback(name='grade_attribution_valid',value=record['grounding_validated'],rationale='Structured negative claims use validated candidate quotes; omissions are anchored to requested requirements. This is not semantic or clinical validation.'),
              Feedback(name='diagnostic_task_fulfilled',value=j['task_fulfilled'],rationale=j['rationale']),
              Feedback(name='fidelity_assessable',value=j['fidelity_status']!='not_assessable',rationale='False means no assessable factual source claim; it is excluded from fidelity-pass aggregation.')]
    if j['fidelity_status']!='not_assessable':feedback.append(Feedback(name='diagnostic_fidelity_pass',value=j['fidelity_status']=='pass',rationale=j['rationale']))
    return feedback
