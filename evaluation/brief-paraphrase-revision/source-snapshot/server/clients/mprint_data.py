"""Read-only, revision-pinned MPRINT public study metadata and classifications."""
import asyncio
import json
from pathlib import Path
import re
import sqlite3
import zlib

DATA = Path(__file__).resolve().parents[1] / 'mc' / 'data'
DATABASE = DATA / 'mprint.sqlite'
OUTCOMES_DATABASE = DATA / 'mprint-outcomes.sqlite'

TYPE_LABELS={'PK':'pharmacokinetics','PE':'pharmacoepidemiology','CT':'clinical trial','PD':'pharmacodynamics','PG':'pharmacogenetics','RCT':'randomized controlled trial','Biomarker':'biomarker','Vaccine':'vaccine','Food, nutrition, and others':'food, nutrition, and other studies'}

def study_codes(text):
    codes=[]
    for code,pattern in [('PK',r'\bPK\b|PKPD|popPK|PBPK|pharmacokinetics'),('PE',r'\bPE\b|pharmacoepidemiology|pharcoepidemiology'),('CT',r'\bCT\b|\bRCT\b|clinical trial'),('PD',r'\bPD\b|PKPD'),('PG',r'\bPG\b'),('RCT',r'\bRCT\b')]:
        if re.search(pattern,text,re.I):codes.append(code)
    return codes

def population_matches(text, population):
    patterns={'pregnancy':r'pregnan|trimester','lactation':r'lactat|breastfeed|breast.fed','pediatric':r'child|pediatric|paediatric|infant|neonat|newborn|adolescen','postpartum':r'postpartum|post.partum','maternal':r'maternal'}
    text=re.sub(r'non[- ]?pregnant','',text,flags=re.I)
    return population=='any' or bool(re.search(patterns[population],text,re.I))


def _connection():
    con = sqlite3.connect(DATABASE.resolve().as_uri() + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    return con


def _base(tier):
    manifest = json.loads((DATA / 'mprint-manifest.json').read_text())
    return {'source': f'snapshot:mprint:{tier}', 'repository_url': manifest['repository'],
            'dataset_revision': manifest['revision'], 'retrieved_at_utc': manifest['retrieved_at_utc'],
            'coverage': manifest['scope'], 'snapshot_is_live': False,
            'outcomes_retrieved_at_utc': manifest.get('outcomes_retrieved_at_utc'),
            'tables_included': [x['path'] for x in manifest.get('files',[])],
            'classification_legend': dict(TYPE_LABELS),
            'guidance_origin': 'Coverage, search, linkage and interpretation caveats are MCP implementation guidance, not quotations from MPRINT dataset authors or original papers.',
            'coverage_notice': 'Versioned export, not the complete live portals. Filters and row limits can omit records; an empty result is not an evidence-gap finding.',
            'curation': 'expert-curated study metadata' if tier=='gold' else 'automated publication classification',
            'caveat': 'Publication inclusion/classification is not proof of efficacy, safety, study quality, or MPRINT funding. Read the original paper. Snapshot absence is not absence of evidence.'}


def _gold(drug, limit, population="any", study_type="any", search_names=None, pmid=None):
    if pmid is not None and not re.fullmatch(r'[1-9][0-9]{0,9}',pmid):
        return {'source':'validation','error':'invalid_pmid','url':'https://www.mprint.org/knowledgebase'}
    tokens = re.findall(r'[^\W_]+', drug.casefold())
    if (not tokens and (pmid is None or drug.strip())) or len(drug)>200:
        return {'source':'validation','error':'invalid_drug','url':'https://www.mprint.org/knowledgebase'}
    if population not in {'any','pregnancy','lactation','pediatric','postpartum','maternal'} or study_type not in {'any','PK','PE','CT','PD','PG','RCT'}:
        return {'source':'validation','error':'invalid_filter','url':'https://www.mprint.org/knowledgebase'}
    names=search_names or ([drug] if tokens else [])
    name_tokens={name:re.findall(r'[^\W_]+',name.casefold()) for name in names}
    out = _base('gold');matches=[]
    con=_connection()
    try:
        sql='SELECT * FROM gold' + (' WHERE pmid=?' if pmid is not None else '') + ' ORDER BY CAST(pmid AS INTEGER) DESC, rowid'
        for row in con.execute(sql,(pmid,) if pmid is not None else ()):
            words=set(re.findall(r'[^\W_]+',row['drug'].casefold()))
            matched=[name for name,parts in name_tokens.items() if parts and all(t in words for t in parts)]
            if tokens and not matched:continue
            if not population_matches(row['population'],population):continue
            codes=study_codes(row['study_type'])
            if study_type!='any' and study_type not in codes:continue
            original=json.loads(row['payload'])
            item={'source_file':original.pop('source_file'), 'source_row':original.pop('source_row'), 'source_fields':original}
            item.update(pmid=row['pmid'],drug_names=row['drug'],population=row['population'],study_type=row['study_type'],
                        study_type_labels=[TYPE_LABELS[k] for k in codes], matched_names=matched,
                        url=f'https://pubmed.ncbi.nlm.nih.gov/{row["pmid"]}/',
                        dataset_url=f'https://github.com/langli-lab/mprint-kp-data/blob/{out["dataset_revision"]}/{item["source_file"]}')
            matches.append(item)
    finally:con.close()
    limit=max(1,min(limit,20));out.update(results=matches[:limit],matching_records=len(matches),returned_records=min(limit,len(matches)),results_truncated=len(matches)>limit,
        applied_filters={'population':population,'study_type':study_type,'pmid':pmid},searched_names=names,
        filter_scope='Conservative matches on source population text; generic maternal does not imply pregnancy or lactation. Original mixed population labels are preserved, not exclusive cohorts.',
        search_scope='Any searched name may match; all tokens of that name must match curated drug fields. Ingredient matches do not establish combination-product evidence. Sorted by descending PMID, not publication date; multiple rows can describe one paper.')
    return out


async def search_gold(drug='', max_results=10, population="any", study_type="any", resolve_names=False, pmid=None):
    if pmid is not None and not re.fullmatch(r'[1-9][0-9]{0,9}',pmid):
        return {'source':'validation','error':'invalid_pmid','url':'https://www.mprint.org/knowledgebase'}
    names=[drug];resolution={'status':'not_requested'}
    if resolve_names and re.findall(r'[^\W_]+',drug) and len(drug)<=200:
        from clients import rxnorm_normalize
        try:
            norm=await rxnorm_normalize(drug)
            resolution={'status':'verified' if norm.get('found') and not norm.get('requires_confirmation') else 'unverified_or_ambiguous','details':norm}
            if norm.get('found') and not norm.get('requires_confirmation'):
                names=list(dict.fromkeys([drug]+norm.get('ingredients',[])))
                resolution['mapping_method']='RxNorm ingredient names matched to Gold name text; RxCUIs are NOT equated with MPRINT UMLS CUIs.'
                if len(norm.get('ingredients',[]))>1:resolution['combination_warning']='Results can concern individual ingredients or other combinations, not necessarily the requested product.'
            elif norm.get('requires_confirmation') and norm.get('found'):
                out=_base('gold');out.update(requires_confirmation=True,resolution=resolution,results=[],note='Confirm the intended generic ingredient; approximate candidates were not searched.')
                return out
        except Exception as exc:
            resolution={'status':'lookup_unavailable','error_type':type(exc).__name__,'note':'Only the literal input name was searched.'}
    out=await asyncio.to_thread(_gold,drug,max_results,population,study_type,names,pmid)
    out['resolution']=resolution
    return out


def _silver(pmids):
    if not pmids or len(pmids)>20 or any(not re.fullmatch(r'[1-9][0-9]{0,9}',p) for p in pmids):
        return {'source':'validation','error':'invalid_pmids','url':'https://www.mprint.org/knowledgebase','note':'Supply 1 to 20 numeric PMID strings.'}
    out=_base('silver');results=[];con=_connection()
    try:
        for pmid in dict.fromkeys(pmids):
            rows=con.execute('SELECT study_type,source_row FROM silver WHERE pmid=? ORDER BY study_type',(pmid,)).fetchall()
            results.append({'pmid':pmid,'found':bool(rows),'classifications':[dict(r,study_type_label=TYPE_LABELS.get(r['study_type'],r['study_type'])) for r in rows],
                            'url':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'})
    finally:con.close()
    out.update(results=results,classification_legend={'PK':'pharmacokinetics','PE':'pharmacoepidemiology','CT':'clinical trial', 'Biomarker':'biomarker', 'Vaccine':'vaccine', 'Food, nutrition, and others':'food, nutrition, and other studies'},
               dataset_url=f'https://github.com/langli-lab/mprint-kp-data/blob/{out["dataset_revision"]}/silver/pmid2study_type.csv',
               limitation='Study-type annotations only. No Silver drug or population mappings loaded. Labels may be multiple and are not human clinical review. Unknown codes are preserved verbatim.')
    return out


async def silver_classifications(pmids):
    return await asyncio.to_thread(_silver,pmids)

def _outcomes(pmid, kind, limit, offset):
    if not re.fullmatch(r'[1-9][0-9]{0,9}',pmid) or kind not in {'any','PE_CT','PK_summary'} or offset<0:
        return {'source':'validation','error':'invalid_outcome_request','url':'https://www.mprint.org/knowledgebase'}
    out=_base('gold');out['curation']='expert-curated aggregate outcome rows'
    limit=max(1,min(limit,20))
    shard=OUTCOMES_DATABASE.with_name(f'{OUTCOMES_DATABASE.stem}-{int(pmid)%2}.sqlite')
    con=sqlite3.connect(shard.resolve().as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
    studies=_connection()
    try:
        context=[dict(r) for r in studies.execute('SELECT * FROM gold WHERE pmid=?',(pmid,))]
        where='pmid=?';args=[pmid]
        if kind!='any':where+=' AND kind=?';args.append(kind)
        count=con.execute('SELECT count(*) FROM outcomes WHERE '+where,args).fetchone()[0]
        rows=con.execute('SELECT * FROM outcomes WHERE '+where+' ORDER BY source_file,source_row LIMIT ? OFFSET ?',args+[limit,offset]).fetchall()
        results=[]
        for row in rows:
            linked=[]
            for study in context:
                data=json.loads(study['payload'])
                if data.get('curation_workbook')!=row['curation_workbook'] or data.get('curation_folder')!=row['curation_folder']:continue
                linked.append({'drug_names':study['drug'],'population':study['population'],'study_type':study['study_type'],
                               'study_type_labels':[TYPE_LABELS[c] for c in study_codes(study['study_type'])],
                               'source_file':data['source_file'],'source_row':data['source_row']})
            results.append({'pmid':pmid,'kind':row['kind'],'source_fields':json.loads(zlib.decompress(row['payload']) if isinstance(row['payload'],bytes) else row['payload']),
                            'source_file':row['source_file'],'source_row':row['source_row'],
                            'url':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',
                            'dataset_url':f'https://github.com/langli-lab/mprint-kp-data/blob/{out["dataset_revision"]}/{row["source_file"]}',
                            'study_context':linked,'study_context_matched':bool(linked)})
    finally:
        con.close();studies.close()
    out.update(results=results,matching_rows=count,returned_rows=len(results),offset=offset,
               next_offset=offset+len(results) if offset+len(results)<count else None,
               results_truncated=offset>0 or offset+len(results)<count,
               guidance_origin='MCP implementation guidance, not a quotation or conclusion from the MPRINT dataset authors or original paper.',
               linkage='This MCP links PMID plus original curation workbook and folder; not an individual cohort/arm or drug-effect join. Do not attribute every row to every drug in study_context.',
               interpretation='Values and uncertainty fields are preserved as source strings. Null means missing in the exported data, not zero; it does not establish that the original paper did not report the field. Describe null as missing in the exported data. Keep statistic, units, exposure/comparator and population context together. No recalculation, pooled estimate or treatment recommendation is provided. Unmatched rows retain source provenance but have no asserted study-context match.',
               limitations='PE/clinical-trial aggregate and PK-summary outcome tables only. Individual-patient outcomes and PK-parameter tables are excluded. Retrieve the original paper to resolve incomplete or inconsistent source fields.')
    return out


async def gold_outcomes(pmid, kind='any', max_results=5, offset=0):
    return await asyncio.to_thread(_outcomes,pmid,kind,max_results,offset)
