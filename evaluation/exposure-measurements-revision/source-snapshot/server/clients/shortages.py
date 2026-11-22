"""FDA public shortage records; no local stock or substitution inference."""
from urllib.parse import urlencode
import re
import httpx
from core.http import http
ENDPOINT='https://api.fda.gov/drug/shortages.json'

async def search_shortages(drug,dosage_form='',status='any',n=10):
    clean=lambda s:' '.join(re.findall(r'[A-Za-z0-9-]+',s))
    q='(generic_name:"'+clean(drug)+'" OR openfda.generic_name:"'+clean(drug)+'" OR openfda.brand_name:"'+clean(drug)+'")'
    if dosage_form:q+=' AND dosage_form:"'+clean(dosage_form)+'"'
    if status!='any':q+=' AND status:"'+status+'"'
    params={'search':q,'limit':n}
    try:data=(await http.request('GET',ENDPOINT,params=params,ttl=3600)).json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code!=404:raise
        data={'results':[],'meta':{}}
    rows=[{k:r.get(k) for k in ['generic_name','company_name','dosage_form','presentation','package_ndc','status','availability','shortage_reason','initial_posting_date','update_date','contact_info']} for r in data.get('results',[])]
    return {'source':'live:openfda:shortages','url':ENDPOINT+'?'+urlencode(params),'results':rows,'last_updated':data.get('meta',{}).get('last_updated'),
        'search_criteria':params,'total_matching_records':data.get('meta',{}).get('results',{}).get('total'),
        'caveat':'FDA product/presentation shortage records, not local pharmacy stock, a substitution recommendation, pediatric suitability or a dosing/safety check. A Current shortage may contain an Available presentation. Read status and availability separately.'}
