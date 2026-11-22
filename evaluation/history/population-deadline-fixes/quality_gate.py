"""Judge calibration must gate use of its scores, never rewrite its verdicts."""
def calibration_gate(records, fixtures):
    expected={f['outputs']['answer']:f['expectations']['expected_judge_pass'] for f in fixtures}
    result={}
    for scorer in ['evidence_fidelity_v2','task_fulfillment_v2']:
        rows=[]
        for r in records:
            answer=r.get('response',{}).get('answer')
            value=r.get(scorer+'/value')
            actual=True if value is True or value=='yes' else False if value is False or value=='no' else None
            rows.append(answer in expected and actual is not None and actual==expected[answer])
        covered={r.get('response',{}).get('answer') for r in records}
        passed=len(rows)==len(expected) and covered==set(expected) and all(rows)
        result[scorer]={'matched_controls':sum(rows),'total_controls':len(expected),'calibration_passed':passed,
            'score_use':'passed_small_control_set_not_clinical_validation' if passed else 'diagnostic_only_do_not_use_as_acceptance_gate'}
    return result

if __name__=='__main__':
    f=[{'outputs':{'answer':'good'},'expectations':{'expected_judge_pass':True}},{'outputs':{'answer':'bad'},'expectations':{'expected_judge_pass':False}}]
    rows=[{'response':{'answer':'good'},'evidence_fidelity_v2/value':'yes','task_fulfillment_v2/value':'no'},{'response':{'answer':'bad'},'evidence_fidelity_v2/value':'no','task_fulfillment_v2/value':'no'}]
    r=calibration_gate(rows,f)
    assert r['evidence_fidelity_v2']['calibration_passed']
    assert not r['task_fulfillment_v2']['calibration_passed']
    assert not calibration_gate(rows[:1],f)['evidence_fidelity_v2']['calibration_passed']
    assert not calibration_gate([],f)['evidence_fidelity_v2']['calibration_passed']
    assert not calibration_gate([rows[0],rows[0]],f)['evidence_fidelity_v2']['calibration_passed']
    print('5 calibration-gate checks passed')
