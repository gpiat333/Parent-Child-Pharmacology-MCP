from pathlib import Path
import csv,hashlib,httpx,io,json,re,sqlite3
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'mc/data';D.mkdir(exist_ok=True)
REV='4bdee90dff3610816e86d0eed29b4c4d0fe76e89';BASE=f'https://raw.githubusercontent.com/langli-lab/mprint-kp-data/{REV}/'
files=['gold/PK/PK_Study_cleaned_cui.csv','gold/PE/PE_CT_Study_info.csv','silver/pmid2study_type.csv']
DB=D/'mprint.sqlite'; con=sqlite3.connect(DB)
con.executescript('DROP TABLE IF EXISTS gold; DROP TABLE IF EXISTS silver; CREATE TABLE gold(pmid TEXT, drug TEXT, population TEXT, study_type TEXT, payload TEXT); CREATE TABLE silver(pmid TEXT, study_type TEXT, source_row INTEGER, PRIMARY KEY(pmid,study_type)) WITHOUT ROWID;')
manifest={'revision':REV,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'repository':'https://github.com/langli-lab/mprint-kp-data','scope':'Gold study metadata only; Silver study-type classifications only. Gold outcome/parameter tables and Silver drug/population mappings not included.','files':[]}
for path in files:
 r=httpx.get(BASE+path,follow_redirects=True,timeout=120);r.raise_for_status();content=r.content
 if content.startswith(b'version https://git-lfs'):raise ValueError('LFS pointer, not data')
 reader=csv.DictReader(io.StringIO(content.decode('utf-8-sig')));count=0;skipped=0
 if path.startswith('gold'):
  drugcol='Drug name' if '/PK/' in path else 'Drug names'
  assert {'PMID',drugcol,'Population','Study type'}.issubset(reader.fieldnames)
  for rowno,row in enumerate(reader,2):
   pmid=row['PMID'].strip()
   if not re.fullmatch(r'[1-9][0-9]{0,9}',pmid):skipped+=1;continue
   payload={k:v.strip() for k,v in row.items() if k in ['PMID',drugcol,'Population','Study type','Species','DOI','Clinical trial ID','study design','sample size','Pregnancy Stage'] and v.strip()}
   payload.update(source_file=path,source_row=rowno)
   con.execute('INSERT INTO gold VALUES(?,?,?,?,?)',(pmid,row[drugcol],row['Population'],row['Study type'],json.dumps(payload)));count+=1
 else:
  assert {'PMID','type'}.issubset(reader.fieldnames)
  for rowno,row in enumerate(reader,2):
   pmid=row['PMID'].strip();kind=row['type'].strip()
   if not re.fullmatch(r'[1-9][0-9]{0,9}',pmid):skipped+=1;continue
   con.execute('INSERT OR IGNORE INTO silver VALUES(?,?,?)',(pmid,kind,rowno));count+=1
 manifest['files'].append({'path':path,'sha256':hashlib.sha256(content).hexdigest(),'input_valid_rows':count,'skipped_invalid_pmids':skipped,'url':BASE+path})
 print(path,count,'valid rows',skipped,'skipped',flush=True)
con.executescript('CREATE INDEX gold_pmid ON gold(pmid);');con.commit()
manifest['gold_rows']=con.execute('SELECT count(*) FROM gold').fetchone()[0];manifest['silver_classifications']=con.execute('SELECT count(*) FROM silver').fetchone()[0];manifest['silver_types']=[r[0] for r in con.execute('SELECT DISTINCT study_type FROM silver')];con.close()
(D/'mprint-manifest.json').write_text(json.dumps(manifest,indent=2))
r=httpx.get(BASE+'LICENSE',timeout=30);r.raise_for_status();(D/'MPRINT-LICENSE.txt').write_text(r.text)
print(json.dumps(manifest,indent=2))
