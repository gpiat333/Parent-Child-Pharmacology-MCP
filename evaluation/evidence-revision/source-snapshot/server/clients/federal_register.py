"""Bounded public-source discovery for parents; no submissions or patient records."""
import asyncio
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from urllib.parse import urlencode, urljoin, urlsplit
import httpx
from core.http import http
import clients as src
from .nichd import Tree
from core.safety import identity_is_vague, contains_identifiers

RECALLS='https://api.fda.gov/drug/enforcement.json'
RECALL_HELP='https://www.fda.gov/drugs/drug-safety-and-availability/drug-recalls'
ALERTS='https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications'
REGISTRIES='https://www.fda.gov/consumers/pregnancy-exposure-registries/list-pregnancy-exposure-registries'
FR='https://www.federalregister.gov/api/v1/documents.json'
DIRECTORIES=[
 {'title':'NIH public involvement','url':'https://www.nih.gov/about-nih/get-involved-nih/public-involvement-nih'},
 {'title':'FDA patient-focused drug development','url':'https://www.fda.gov/drugs/development-approval-process-drugs/cder-patient-focused-drug-development'}]

from .parent_common import now, term, limit, links

def input_row(r,today=None):
    today=today or date.today();deadline=r.get('comments_close_on')
    try:
        parsed=date.fromisoformat(deadline)
        relation='past' if parsed<today else 'today' if parsed==today else 'future'
        status='closed' if relation=='past' else 'deadline_not_passed_verify_notice'
        summary=f'Listed comment deadline: {parsed.isoformat()} ({relation} relative to {today.isoformat()}). Submission acceptance has not been verified.'
    except (ValueError,TypeError):
        parsed=None;relation='unknown';status='deadline_unknown_verify_notice'
        summary='Comment deadline unknown in the returned data. Meeting dates do not establish whether comments are open or closed.'
    return {k:r.get(k) for k in ['title','document_number','publication_date','abstract','html_url','pdf_url','comments_close_on','comment_url','dates','addresses','agencies']} | {
        'participation_status':status,'submission_performed':False,
        'comment_deadline':{'date':parsed.isoformat() if parsed else None,'date_known':parsed is not None,'relation_to_as_of':relation,'as_of':today.isoformat(),'source_field':'comments_close_on','time_of_day_known':False},
        'submission_status':'not_verified','submission_open_confirmed':False,
        'meeting_dates_used_for_deadline':False,'deadline_summary':summary,
        'status_interpretation':'Legacy participation_status closed means listed comment deadline has passed, not independently verified portal closure. Use comment_deadline for date grouping; submission status and relevance are separate.'}

async def input_opportunities(topic,agency='NIH',max_results=10):
    topic=term(topic)
    agencies={'NIH':'national-institutes-of-health','FDA':'food-and-drug-administration'}
    clean=' '.join(re.findall(r'\w+',topic))
    if not clean:raise ValueError('Use a topic with words')
    # Federal Register's search syntax must not be treated like PubMed/Lucene.
    # Simple subject search plus local candidate checks avoids false empty results.
    params={'conditions[term]':clean,'conditions[agencies][]':agencies[agency],'order':'relevance','per_page':50}
    data=(await http.request('GET',FR,params=params,ttl=900)).json()
    candidates=[r for r in data.get('results',[]) if is_input_candidate(r)]
    enriched=[]
    for row in candidates[:limit(max_results)]:
        number=row.get('document_number','')
        if re.fullmatch(r'\d{4}-\d+',number):
            try:
                detail=(await http.request('GET',f'https://www.federalregister.gov/api/v1/documents/{number}.json',ttl=900)).json()
                row={**row,**detail}
            except Exception:
                row={**row,'detail_unavailable':True}
        item=input_row(row)
        item['detail_unavailable']=row.get('detail_unavailable',False)
        item['relevance']=topic_support(topic,{'title':row.get('title',''),'abstract':row.get('abstract','')})
        item['relevance_note']='Search candidate, not verified audience fit. Label indirect_or_unverified results as broader/indirect; a topic match does not establish that the notice seeks parent input.'
        enriched.append(item)
    return {'source':'live:federalregister','url':FR+'?'+urlencode(params),'queried_at_utc':now(),'cache_max_age_seconds':900,
            'notices':enriched,'directories':DIRECTORIES,
            'matching_candidates_in_page':len(candidates),
            'limitations':['Topic-matched notices are candidates, not necessarily requests for public input. Verify the notice text, deadline, submission method and audience.',
              'Does not cover every NIH RFI, listening session or FDA meeting. Missing deadline is unknown, not open. No comments submitted.',
              'Public comments may be public; do not include personal medical histories or identifiers. FederalRegister.gov is not the official legal edition; verify the linked official PDF.']}

def is_input_candidate(row):
    title=row.get('title','').lower()
    if 'closed meeting' in title:return False
    text=title+' '+(row.get('abstract') or '').lower()
    return bool(row.get('comment_url') or row.get('comments_close_on') or re.search(r'request for (?:information|input|comments)|public (?:comment|meeting|input)|listening session',text))

from .trial_navigation import topic_support
