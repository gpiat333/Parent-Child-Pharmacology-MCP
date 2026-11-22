"""Versioned, narrow checks for approved fixed refusals, not clinical correctness."""
APPROVED={
 'personal':'I cannot provide an individualized medication decision, dose, missed-dose instruction, schedule, or taper plan. Please contact your prescribing clinician or pharmacist for an individualized plan.',
 'identity':'I cannot identify a medicine from its appearance or a vague description. Check the exact name, formulation and ingredients on the package with a pharmacist before researching it.'
}
FOOTER='Informational only; not medical advice. Patients should talk to a clinician, pharmacist or poison control before starting, stopping or changing any medication.'
def refusal_contract(answer,kind,completed,tool_count,model_calls):
 if kind not in APPROVED:return False
 expected=APPROVED[kind]+'\n\n'+FOOTER
 return bool(completed and tool_count==0 and model_calls==0 and answer.strip()==expected)

if __name__=='__main__':
 count=0
 for kind,text in APPROVED.items():
  answer=text+'\n\n'+FOOTER
  assert refusal_contract(answer,kind,True,0,0);count+=1
  for bad in [answer+' You should stop the medicine.',answer.replace(text,'You can take it.'),'',answer.replace(FOOTER,'')]:
   assert not refusal_contract(bad,kind,True,0,0);count+=1
  assert not refusal_contract(answer,kind,False,0,0);count+=1
  assert not refusal_contract(answer,kind,True,1,0);count+=1
  assert not refusal_contract(answer,kind,True,0,1);count+=1
 print(f'{count} refusal-contract controls passed')
