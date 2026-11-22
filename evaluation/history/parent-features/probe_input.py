import asyncio,json,sys
from pathlib import Path
sys.path.insert(0,r'C:\Users\piatkowskigs\Documents\mcp-mother-child')
from mc import parent_resources as p
async def main():
 params={'conditions[term]':'clinical research','conditions[agencies][]':'national-institutes-of-health','order':'relevance','per_page':50}
 d=(await p.http.request('GET',p.FR,params=params)).json()
 print('total',d.get('count'),'returned',len(d.get('results',[])),flush=True)
 rows=[r for r in d.get('results',[]) if p.is_input_candidate(r)]
 print('candidates',[(r['title'],r.get('comments_close_on'),r.get('document_number')) for r in rows[:5]],flush=True)
 Path(__file__).with_name('public-input-probe.json').write_text(json.dumps(d,indent=2))
asyncio.run(main())
