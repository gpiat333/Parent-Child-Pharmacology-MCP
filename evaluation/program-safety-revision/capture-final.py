from pathlib import Path
import json,sys
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/program-safety-revision';sys.path.insert(0,str(R))
from paired_evaluation import MCP,save
m=MCP()
try:
 save(R/'inventory.json',{k:m.rpc(k+'/list',{}) for k in ['tools','prompts','resources']})
finally:m.close()
s=(Path(__file__).parent/'probe-current.py').read_text().replace("P/'evaluation/evidence-revision'","P/'evaluation/program-safety-revision'").replace("Path(__file__).parent/'protocol-probes'","P/'evaluation/program-safety-revision/protocol-probes'").replace("'drug':'amoxicillin','max_results':3","'drug':'rocuronium','max_results':3")
exec(compile(s,'capture-protocols','exec'))
m=MCP()
try:
 for cid,name,args in [('empty','get_mprint_details',{'pmids':['99999999'],'table':'gold'}),('registry','find_pregnancy_exposure_registries',{'drug':'daridorexant'}),('gap-brief','medication_evidence_brief',{'drug':'daridorexant','population':'pregnancy'}),('clinician-questions','medication_evidence_brief',{'drug':'amoxicillin','population':'lactation'})]:
  try:save(R/(cid+'.json'),m.call(name,args));print(cid,flush=True)
  except Exception as e:print(cid,type(e).__name__,flush=True)
finally:m.close()
