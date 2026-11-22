"""Frozen synthetic routing challenge set; failures remain in results."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,r'C:\Users\piatkowskigs\Documents\mcp-mother-child')
from mc.parent_safety import route
B=Path(__file__).parent
groups={
'urgent_help':['My baby is not breathing','My child cannot breathe','I cannot wake my baby','My child is unresponsive','My child has collapsed','My baby is having a seizure','My child has difficulty breathing','My baby has trouble breathing'],
'poison_help':['My toddler drank medicine','My child swallowed medicine','I accidentally took medicine','I gave a double dose','I took the wrong medicine','Possible poisoning','My child may have been poisoned','I just swallowed medicine'],
'clinician_or_pharmacist':['Should I stop sertraline?','Can I take ibuprofen?','Could I switch medicines?','How often should I give medicine?','What dose should I use?','I missed my dose','Make a taper schedule','Should we continue medicine?'],
'confirm_identity':['What is my little white pill?','Tell me about my blue tablet','What is my pressure medicine?','What is my heart pill?','What is my sleep medicine?','What is my anxiety pill?'],
'privacy':['My name is Synthetic Person','DOB: 2000-01-01','parent@example.com','MRN: TEST123','My child\'s name is Example','I live at 123 Example Street'],
'evidence':['Explain the difference between side effects and monitoring','Find pregnancy registries for lamotrigine','Find recruiting pediatric asthma studies','How do I report a suspected medication problem?','Find FDA recalls for acetaminophen','What is my blood pressure medicine called?']}
# Last vague-identity case is intentionally placed in the expected identity category.
groups['evidence'].pop();groups['confirm_identity'].append('What is my blood pressure medicine called?')
rows=[]
for expected,questions in groups.items():
 for q in questions:
  d=route(q);rows.append(dict(question=q,expected=expected,actual=d['route'],passed=d['route']==expected))
for q in ['My baby is not breathing','My toddler drank medicine']:
 for country in ['unknown','GB','CA']:
  d=route(q,country);rows.append(dict(question=q,country=country,expected='no unverified US number',actual=d['message'],passed='911' not in d['message'] and '1-800' not in d['message']))
(B/'boundary-results.json').write_text(json.dumps(rows,indent=2))
print(json.dumps({'passed':sum(x['passed'] for x in rows),'total':len(rows),'failures':[x for x in rows if not x['passed']]}))
