"""Cross-source evidence preparation with explicit ingredient coverage."""
import asyncio
import clients as src
from models.contracts import *
from models.inputs import Population
from core.evidence import annotate, clinician_questions
from core.population import preserve_population
from core.response import urls
from .lactation import search_lactmed, get_lactmed_record
from .labels_safety import get_label_sections, get_adverse_event_signals, get_patient_education
from .literature import search_literature, search_trials
from .literature import get_abstracts
from core.evidence_axes import build_axes, AXES
from core.participation import tier
from core.abstract_coverage import coverage, merge_coverages
from clients import parent_resources as parents

async def medication_evidence_brief(drug: Query, population: Population = 'lactation') -> EvidenceResponse:
    """Use for explicit requests to prepare an evidence brief, including pregnancy briefs.
    Call before optional individual source lookups when preflight requested_workflow
    requires it. Compile public evidence and questions to ask a clinician, never a safety verdict.
    Normalize the exact product then search EACH confirmed active ingredient. Keep
    ingredient evidence separate; combined effects and interactions are not established.
    Preserve requested age band, source ages, missing evidence, dose flags and pregnancy limits.
    Prefer get_parent_medication_info for focused medicine-taker versus infant findings.
    Includes literature metadata and abstract_coverage. Disclose missing abstract text,
    unreturned records and retrieval failures; preserve required_display_notices.
    Metadata and titles alone cannot support study-outcome claims.
    Display FAERS report_only_context separately, even when observed-outcome rows
    are empty. Report counts are unconfirmed signals, not established outcomes."""
    norm=await src.rxnorm_normalize(drug)
    base=preserve_population({'source':'composite','drug_input':drug,'resolved':norm,
        'questions_to_ask_clinician':clinician_questions(population)},population)
    if not norm.get('found') or norm.get('requires_confirmation') or not norm.get('ingredients'):
        return annotate({**base,'requires_confirmation':True,
            'participation':tier(suppressed=True,reason='unconfirmed_identity'),
            'note':'Confirm the exact medicine and every active ingredient before evidence retrieval.'})
    ingredients=list(dict.fromkeys(norm['ingredients']))
    async def ingredient(name):
        async def literature():
            first=await search_literature(name,population,5,'keyword')
            searches=[first]
            if population=='pregnancy': searches.append(await search_literature(name,population,3,'keyword','maternal_pharmacokinetics'))
            metadata=list({r['pmid']:r for search in searches for r in search.get('results',[]) if r.get('pmid')}.values())
            fetched=await get_abstracts([r['pmid'] for r in metadata[:10]]) if metadata else {'articles':[], 'abstract_coverage':coverage([],[])}
            return {**first,'results':metadata,'articles':fetched.get('articles',[]),'searches':searches,
                    'abstract_coverage':fetched['abstract_coverage'],
                    **({'error':fetched['error']} if fetched.get('error') else {}),
                    'coverage_notice':'Bounded relevance search and abstracts only, not a systematic review. Titles alone are not outcome evidence.'}
        async def lactmed():
            if population!='lactation': return {'status':'not_applicable','note':'LactMed applies to lactation.'}
            hit=await search_lactmed(name,3)
            rows=hit.get('results',[])
            if len(rows)==1: return await get_lactmed_record(rows[0]['id'],16000)
            return {'results':rows,'requires_record_selection':bool(rows),
                    'note':'Select the matching ingredient record.' if rows else 'No LactMed evidence retrieved.'}
        cohort={'pregnancy':'pregnancy','infant':'infant'}.get(population,'any')
        keys=['lactmed','label','literature','adverse_events','trials','patient_info']
        values=await asyncio.gather(lactmed(),get_label_sections(name),
            literature(),
            get_adverse_event_signals(name,cohort,8),search_trials(name,population,5),
            get_patient_education(name),return_exceptions=True)
        row={k:({'error':'source_unavailable'} if isinstance(v,Exception) else v) for k,v in zip(keys,values)}
        if row['literature'].get('error') and not row['literature'].get('abstract_coverage'):
            row['literature']['abstract_coverage']=coverage([],[],search_failed=True)
        row['ingredient']=name
        row['evidence_axes'],pk=build_axes(row,population)
        if population=='pregnancy':
            row['maternal_pharmacokinetics']=pk
            row['maternal_dose_adjustment']=row['label'].get('pllr_8_1',{}).get('maternal_dose_adjustment',
                {'clinical_considerations_text':None,'dose_adjustment_text':None,'dose_adjustment_data_found':False,'source_context_only':True})
            try: registry=await parents.pregnancy_registries(name,20)
            except Exception: registry={'error':'source_unavailable','results':[]}
            try: recruiting=await parents.recruiting_studies(name,population,'',5)
            except Exception: recruiting={'error':'source_unavailable','studies':[]}
            row['participation']=tier({'registries':registry,'recruiting_studies':recruiting,
                'public_input_notices':{'status':'not_searched','results':[],'tool':'search_parent_input_opportunities',
                                       'note':'Available separately by research topic; no drug-specific notice inferred.'}})
        row['adverse_events']['requested_population']=population
        row['adverse_events']['matches_requested_age_band']=False
        row['adverse_events']['population_notice']='FAERS age coverage is not the requested pediatric band; do not generalize these counts to it.' if population in {'neonate','infant','child','adolescent','pediatric'} else 'Report-query coverage, not a complete exposed population.'
        return annotate(row)
    rows=[]
    for name in ingredients: rows.append(await ingredient(name))
    out={**base,'queried_ingredients':ingredients,'ingredient_evidence':rows,
         'abstract_coverage':merge_coverages([r['literature']['abstract_coverage'] for r in rows]),
         'evidence_axis_order':list(AXES),
         'display_contract':'Always render all three evidence-axis rows, including empty rows. Also show any report_only_context separately as unconfirmed spontaneous-report terms and counts, with the query scope, source link and population uncertainty. An empty observed-outcomes row does not mean no human reports were retrieved. Report counts are not established outcomes or rates. Participation is a separate unranked navigation tier, never evidence of safety.',
         'ingredient_coverage':{'all_normalized_ingredients_queried':True,
            'interaction_assessment_performed':False,'combined_product_safety_established':False},
         'warning':'Ingredient searches do not establish combination-product safety or interactions.'}
    out['evidence_axes']=[{'axis':key,'label':label,'by_ingredient':[{'ingredient':r['ingredient'],**next(a for a in r['evidence_axes'] if a['axis']==key)} for r in rows]} for key,label in AXES.items()]
    if population=='pregnancy': out['maternal_pharmacokinetics']=[{'ingredient':r['ingredient'],**r['maternal_pharmacokinetics']} for r in rows]
    out['citations']=list(dict.fromkeys(urls(rows)))
    return annotate(out)
