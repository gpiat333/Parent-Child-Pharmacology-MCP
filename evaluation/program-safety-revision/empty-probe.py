from pathlib import Path
import sys
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20');R=P/'evaluation/program-safety-revision';sys.path.insert(0,str(R))
from paired_evaluation import MCP,save
m=MCP()
try:
 r=m.call('search_lactmed',{'drug':'zzprototypeNoMatchCompound2026zz','max_results':1});save(R/'empty.json',r)
 assert r['result']['evidence_status']['no_evidence_retrieved'] and r['result']['evidence_status']['not_evidence_of_safety'];print('Empty result contract verified')
finally:m.close()
