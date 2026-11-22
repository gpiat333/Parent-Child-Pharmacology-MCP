from pathlib import Path
import sqlite3
D=Path(__file__).resolve().parents[1]/'mc/data';source=D/'mprint-outcomes.sqlite';c=sqlite3.connect(source);total=c.execute('select count(*) from outcomes').fetchone()[0];copied=0
for shard in range(2):
 p=D/f'mprint-outcomes-{shard}.sqlite';o=sqlite3.connect(p)
 o.executescript('DROP TABLE IF EXISTS outcomes;CREATE TABLE outcomes(pmid TEXT,kind TEXT,source_file TEXT,source_row INTEGER,curation_workbook TEXT,curation_folder TEXT,payload BLOB);')
 o.executemany('INSERT INTO outcomes VALUES(?,?,?,?,?,?,?)',c.execute('SELECT * FROM outcomes WHERE CAST(pmid AS INTEGER)%2=?',(shard,)))
 o.execute('CREATE INDEX outcome_pmid ON outcomes(pmid)');o.commit();n=o.execute('select count(*) from outcomes').fetchone()[0];copied+=n;assert o.execute('PRAGMA integrity_check').fetchone()[0]=='ok';o.close();print(shard,n,p.stat().st_size)
assert total==copied;c.close();source.unlink()
