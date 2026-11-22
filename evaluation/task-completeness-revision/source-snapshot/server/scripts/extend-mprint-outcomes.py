from pathlib import Path
from datetime import datetime,timezone
import csv,io,json,sqlite3,httpx,hashlib,sys,zlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mc.mprint_outcomes import parse_outcomes
D=ROOT/'mc/data';m=json.loads((D/'mprint-manifest.json').read_text());base=f'https://raw.githubusercontent.com/langli-lab/mprint-kp-data/{m["revision"]}/'
c=sqlite3.connect(D/'mprint.sqlite')
for path in ['gold/PK/PK_Study_cleaned_cui.csv','gold/PE/PE_CT_Study_info.csv']:
 r=httpx.get(base+path,timeout=120);r.raise_for_status()
 rows=list(csv.DictReader(io.StringIO(r.content.decode('utf-8-sig'))))
 for rid,payload in c.execute('SELECT rowid,payload FROM gold').fetchall():
  obj=json.loads(payload)
  if obj['source_file']!=path:continue
  original=rows[obj['source_row']-2]
  obj['curation_workbook']=original['_source_file'];obj['curation_folder']=original['_source_folder']
  c.execute('UPDATE gold SET payload=? WHERE rowid=?',(json.dumps(obj),rid))
c.commit()
o=sqlite3.connect(D/'mprint-outcomes.sqlite');o.executescript('DROP TABLE IF EXISTS outcomes; CREATE TABLE outcomes(pmid TEXT,kind TEXT,source_file TEXT,source_row INTEGER,curation_workbook TEXT,curation_folder TEXT,payload TEXT);')
files=[]
for kind,path in [('PE_CT','gold/PE/PE_CT_Outcomes.csv'),('PK_summary','gold/PK/PK_Outcomes_summary.csv')]:
 r=httpx.get(base+path,timeout=120);r.raise_for_status();count=skipped=unlinked=0
 for row in parse_outcomes(r.content,kind):
  if not row['pmid']:skipped+=1;continue
  # Keep explicit unmatched rows, but never invent a study association.
  linked=False
  for (payload,) in c.execute('SELECT payload FROM gold WHERE pmid=?',(row['pmid'],)):
   study=json.loads(payload)
   if study.get('curation_workbook')==row['curation_workbook'] and study.get('curation_folder')==row['curation_folder']:linked=True
  if not linked:unlinked+=1
  o.execute('INSERT INTO outcomes VALUES(?,?,?,?,?,?,?)',(row['pmid'],kind,path,row['source_row'],row['curation_workbook'],row['curation_folder'],zlib.compress(json.dumps(row['source_fields']).encode('utf-8'))))
  count+=1
 files.append({'path':path,'sha256':hashlib.sha256(r.content).hexdigest(),'url':base+path,'included_rows':count,'skipped_invalid_pmids':skipped,'rows_without_matching_study_context':unlinked})
 print(kind,count,'rows',skipped,'invalid',unlinked,'unlinked',flush=True)
o.execute('CREATE INDEX outcome_pmid ON outcomes(pmid)');o.commit();print('integrity',o.execute('PRAGMA integrity_check').fetchone());o.close();c.close()
m['files']=[x for x in m['files'] if x['path'] not in {v['path'] for v in files}]+files
m['scope']='Gold study metadata and aggregate PE/CT and PK-summary outcome rows; Silver automated study-type labels. Individual-patient outcomes, PK parameter tables and Silver drug/population mappings excluded.'
m['outcomes_retrieved_at_utc']=datetime.now(timezone.utc).isoformat()
m['outcome_rows']=sum(f['included_rows'] for f in files)
(D/'mprint-manifest.json').write_text(json.dumps(m,indent=2))
print('Database bytes',[(p.name,p.stat().st_size) for p in D.glob('*.sqlite')])

# Keep each deployed source file below Databricks file-size limits.
exec((Path(__file__).parent / "split-mprint-outcomes.py").read_text())
