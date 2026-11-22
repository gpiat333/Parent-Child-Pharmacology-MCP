from paired_evaluation import MCP,HERE,save
m=MCP()
cases=[
 ('empty','search_lactmed',{'drug':'SYNTHETIC-ZZNOEVIDENCE-QZX'}),
 ('registry','find_pregnancy_exposure_registries',{'drug':'daridorexant'}),
 ('label-pllr','get_label_sections',{'drug':'lamotrigine'}),
 ('curated-lactation','search_literature',{'query':'sertraline','population':'lactation','focus':'exposure','mode':'keyword','max_results':3}),
 ('spanish-education','get_patient_education',{'topic':'What information is available in Spanish for sertraline?','rxcui':'36437','language':'es'}),
]
try:
 for cid,name,args in cases:
  d=m.call(name,args);save(HERE/(cid+'.json'),{'id':cid,'tool':name,'arguments':args,'payload':d['result'],'elapsed_ms':d['latency_ms'],'endpoint':'http://127.0.0.1:18080/mcp'})
  print(cid,d['result'].get('status'),flush=True)
finally:m.close()
