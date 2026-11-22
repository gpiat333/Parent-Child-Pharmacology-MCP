"""Inspect real FastMCP argument models without calling external data services."""
import asyncio
import importlib.metadata
import json
from pathlib import Path
import sys

ROOT = Path(r'C:\Users\piatkowskigs\Documents\mcp-mother-child')
sys.path.insert(0, str(ROOT))
import server
from pydantic import BaseModel, ValidationError

CASES = [
 ('valid population', 'search_literature', {'query':'sertraline','population':'lactation'}),
 ('invalid population', 'search_literature', {'query':'sertraline','population':'adult'}),
 ('invalid network', 'search_nichd_studies', {'network':'other'}),
 ('invalid agency', 'search_parent_input_opportunities', {'topic':'research','agency':'CDC'}),
 ('missing drug', 'search_lactmed', {}),
 ('wrong drug type', 'search_lactmed', {'drug':123}),
 ('wrong list item type', 'get_abstracts', {'pmids':[123]}),
 ('noninteger limit', 'search_lactmed', {'drug':'sertraline','max_results':'many'}),
 ('negative limit', 'search_lactmed', {'drug':'sertraline','max_results':-1}),
 ('oversized limit', 'search_lactmed', {'drug':'sertraline','max_results':9999}),
 ('empty drug', 'search_lactmed', {'drug':''}),
 ('extra field', 'search_lactmed', {'drug':'sertraline','unexpected':True}),
 ('numeric string coercion', 'search_lactmed', {'drug':'sertraline','max_results':'5'}),
 ('nonnumeric record ID', 'get_lactmed_record', {'book_id':'sertraline'}),
 ('empty ID list', 'get_abstracts', {'pmids':[]}),
]

async def main():
    registered={t.name:t for t in server.mcp._tool_manager.list_tools()}
    rows=[]
    for label,name,args in CASES:
        async def capture(**validated):
            return validated
        try:
            result=await registered[name].fn_metadata.call_fn_with_arg_validation(capture,True,args,None)
            rows.append({'case':label,'tool':name,'input':args,'schema_accepted':True,'validated':result})
        except ValidationError as e:
            rows.append({'case':label,'tool':name,'input':args,'schema_accepted':False,'errors':[x['type'] for x in e.errors()]})
    report={'date':'2026-11-20','scope':'Local registered FastMCP validation path; capture callback replaces retrieval. No deployed or clinical validation.',
      'versions':{k:importlib.metadata.version(k) for k in ['mcp','pydantic']},
      'tools':[{'name':t.name,'pydantic_model':issubclass(t.fn_metadata.arg_model,BaseModel),'input_schema':t.parameters,'output_schema':t.output_schema,'description':t.description} for t in registered.values()],
      'probes':rows}
    Path(__file__).with_name('results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'tools':len(registered),'probes':rows},indent=2))

asyncio.run(main())
