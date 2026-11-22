"""RePORTER v2 project searches and bounded fiscal-year aggregates."""
from collections import defaultdict
from decimal import Decimal
from core.http import http
from core.research_filters import IC_AGENCIES

REPORTER = "https://api.reporter.nih.gov/v2/projects/search"

class ProjectRows(list):
    def __init__(self,rows,metadata):super().__init__(rows);self.search_metadata=metadata

def reporter_criteria(text,ic='any',fiscal_years=None,activity_code='',organization=''):
    c={'advanced_text_search':{'operator':'and','search_field':'all','search_text':text},'exclude_subprojects':True}
    if ic!='any':c.update(agencies=[IC_AGENCIES[ic]],is_agency_admin=True)
    if fiscal_years:c['fiscal_years']=list(dict.fromkeys(fiscal_years))
    if activity_code:c['activity_codes']=[activity_code]
    if organization:c['org_names']=[organization]
    return c

def project(p):
    a=p.get('agency_ic_admin') or {}
    return {'appl_id':p.get('appl_id'),'project_num':p.get('project_num'),'core_project_num':p.get('core_project_num'),
        'title':p.get('project_title'),'fiscal_year':p.get('fiscal_year'),'institute':a.get('abbreviation'),'ic_code':a.get('code'),
        'activity_code':p.get('activity_code'),'organization':(p.get('organization') or {}).get('org_name'),
        'award_amount_usd':p.get('award_amount'),'direct_cost_usd':p.get('direct_cost_amt'),'indirect_cost_usd':p.get('indirect_cost_amt'),
        'abstract':(p.get('abstract_text') or '')[:2000],'abstract_truncated':len(p.get('abstract_text') or '')>2000,
        'url':p.get('project_detail_url'),'amount_basis':'RePORTER fiscal-year award obligations in USD; not lifetime project value. Total award includes indirect costs; direct costs are separate.'}

async def reporter_page(criteria,offset,n):
    body={'criteria':criteria,'offset':offset,'limit':n,'sort_field':'fiscal_year','sort_order':'desc',
        'include_fields':['ApplId','CoreProjectNum','ProjectNum','ProjectTitle','FiscalYear','AgencyIcAdmin','ActivityCode','AwardAmount','DirectCostAmt','IndirectCostAmt','Organization','ProjectDetailUrl','AbstractText']}
    data=(await http.request('POST',REPORTER,json=body,interval=1.0)).json()
    return [project(p) for p in data.get('results',[])],data.get('meta',{})

async def reporter_search(text,n=10,ic='any',fiscal_years=None,activity_code='',organization=''):
    criteria=reporter_criteria(text,ic,fiscal_years,activity_code,organization)
    rows,meta=await reporter_page(criteria,0,n)
    return ProjectRows(rows,{'criteria':criteria,'total_matching_records':meta.get('total'),'returned_records':len(rows),
        'source_search_url':meta.get('search_url') or meta.get('url'),'bounded_result_set':meta.get('total',len(rows))>len(rows)})

def aggregate_projects(rows):
    groups={};seen=set();duplicates=0
    for position,p in enumerate(rows):
        identity=(p.get('appl_id') or p.get('project_num') or ('unidentified',position),p.get('fiscal_year'))
        if identity in seen:duplicates+=1;continue
        seen.add(identity);key=(p.get('ic_code'),p.get('institute'),p.get('fiscal_year'))
        g=groups.setdefault(key,{'ic_code':key[0],'institute':key[1],'fiscal_year':key[2],'project_records':0,'core_projects':set(),'missing_core_project_id_records':0,'amounts':defaultdict(list),'missing_amount_records':defaultdict(int),'activity_counts':defaultdict(int)})
        g['project_records']+=1;g['activity_counts'][p.get('activity_code') or 'unknown']+=1
        if p.get('core_project_num'):g['core_projects'].add(p['core_project_num'])
        else:g['missing_core_project_id_records']+=1
        for field in ['award_amount_usd','direct_cost_usd','indirect_cost_usd']:
            v=p.get(field)
            if v is None:g['missing_amount_records'][field]+=1
            else:g['amounts'][field].append(Decimal(str(v)))
    result=[]
    for _,g in sorted(groups.items(),key=lambda kv:tuple(str(v or '') for v in kv[0])):
        amounts=g.pop('amounts');g['distinct_core_projects']=len(g.pop('core_projects'));g['totals_usd']={k:float(sum(amounts[k],Decimal(0))) if amounts[k] else None for k in ['award_amount_usd','direct_cost_usd','indirect_cost_usd']}
        g['missing_amount_records']=dict(g['missing_amount_records']);g['activity_counts']=dict(g['activity_counts']);result.append(g)
    return result,duplicates

async def research_portfolio(topic,ic='any',fiscal_years=None,activity_code='',organization='',max_projects=200):
    criteria=reporter_criteria(topic,ic,fiscal_years,activity_code,organization);rows=[];total=None;source_url=None
    while len(rows)<max_projects:
        page,meta=await reporter_page(criteria,len(rows),min(100,max_projects-len(rows)))
        total=meta.get('total');source_url=meta.get('search_url') or meta.get('url') or source_url
        if not page:break
        rows.extend(page)
        if total is not None and len(rows)>=total:break
    groups,duplicates=aggregate_projects(rows)
    complete=total is not None and len(rows)>=total
    year_coverage=[]
    for year in dict.fromkeys(fiscal_years or []):
        year_groups=[g for g in groups if g['fiscal_year']==year]
        count=sum(g['project_records'] for g in year_groups)
        year_coverage.append({'fiscal_year':year,'administering_ic_filter':ic,
            'retrieved_project_records':count,'portfolio_project_records':count if complete else None,
            'complete_result_set':complete,
            'interpretation':'Count in the retrieved extract only. Zero does not establish zero projects in the full portfolio unless the result set is complete.'})
        if not year_groups and ic!='any':
            groups.append({'ic_code':ic,'institute':IC_AGENCIES[ic],'fiscal_year':year,
                'project_records':0,'distinct_core_projects':0,'missing_core_project_id_records':0,
                'totals_usd':{k:None for k in ['award_amount_usd','direct_cost_usd','indirect_cost_usd']},
                'missing_amount_records':{},'activity_counts':{},'empty_in_retrieved_extract':True,
                'portfolio_project_records':0 if complete else None,
                'interpretation':'No records for this requested IC/year in the retrieved extract. Amounts are unavailable, not zero funding; a capped result cannot establish a zero portfolio count.'})
    groups.sort(key=lambda g:(str(g['ic_code'] or ''),str(g['fiscal_year'] or '')))
    return {'source':'live:reporter','url':source_url or 'https://reporter.nih.gov/','query_criteria':criteria,'groups':groups,
        'requested_year_coverage':year_coverage,
        'retrieved_project_records':len(rows),'total_matching_records':total,'duplicate_records_removed':duplicates,
        'complete_result_set':complete,'aggregation_scope':'Retrieved application/fiscal-year records only, grouped by administering IC; subprojects excluded to reduce double counting. Display every requested year, including zero retrieved records, while keeping full-portfolio counts unknown when capped.',
        'amount_basis':'Fiscal-year obligations in USD, not total project value. Award amounts and direct costs are separate sums. Unknown amounts remain missing, not zero. Administering IC grouping is not attribution of every funding IC contribution.',
        'coverage_caveats':['A capped search is not a complete portfolio. Narrow filters when complete_result_set is false.','Activity codes identify funding mechanisms; they do not by themselves establish sustained investment, completed findings or grant performance.','Organization names use the upstream partial-name match. Multi-year and fiscal-year accounting require source review.','Reported award, direct and indirect amounts can differ in accounting basis and need not reconcile. Preserve source values; do not derive missing amounts by subtraction.'],
        'aggregation_application_ids':[p.get('appl_id') for p in rows],
        'projects':rows[:10],'projects_are_samples':len(rows)>10,'sample_scope':'At most ten project details; aggregates use all retrieved records and retain application IDs.'}
