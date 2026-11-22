"""Two explicit interfaces to published MPRINT snapshots, not inferred keyword membership."""
from clients import mprint_data
from models.contracts import *
from models.inputs import Population
from core.population import preserve_population

async def find_mprint_records(drug: OptionalQuery = '', pmid: PMID | None = None,
    population: Population = 'any', study_type: Literal['any','PK','PE','CT','PD','PG','RCT'] = 'any',
    max_results: Limit20 = 10, resolve_names: bool = True) -> EvidenceResponse:
    """Find curated Gold study metadata by drug or exact PMID; one selector is required.
    If both supplied, both must match. Follow with get_mprint_details for outcomes.
    Snapshot inclusion is not proof of safety, quality, or MPRINT funding.
    Age-band requests preserve the requested band; broad source labels are not age-band confirmation."""
    if not drug and not pmid: return {'source':'validation','error':'selector_required'}
    broad = 'pediatric' if population in {'neonate','infant','child','adolescent'} else population
    out = await mprint_data.search_gold(drug,max_results,broad,study_type,resolve_names,pmid)
    return preserve_population(out,population)

async def get_mprint_details(pmid: PMID,
    table: Literal['gold_outcomes','gold_PE_CT','gold_PK_summary','silver_classifications'] = 'gold_outcomes',
    max_results: Limit20 = 5, offset: Offset = 0) -> EvidenceResponse:
    """Get aggregate curated Gold outcomes OR automated Silver classifications by PMID.
    Select table explicitly; Silver labels are not curated Gold clinical findings.
    Gold null means missing in exported data, not zero. Context joins are by PMID and workbook,
    not cohort or treatment arm; do not assign every outcome to every drug. Doses are source
    observations, never recommendations. No individual-patient data. Preserve snapshot provenance.
    Silver returns the single-PMID classification lookup; max_results/offset apply to Gold only."""
    if table == 'silver_classifications':
        out = await mprint_data.silver_classifications([pmid])
    else:
        kind={'gold_outcomes':'any','gold_PE_CT':'PE_CT','gold_PK_summary':'PK_summary'}[table]
        out = await mprint_data.gold_outcomes(pmid,kind,max_results,offset)
    return {**out,'requested_table':table,'pmid':pmid}
