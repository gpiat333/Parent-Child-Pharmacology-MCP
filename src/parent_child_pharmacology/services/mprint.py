"""Two explicit interfaces to published MPRINT snapshots, not inferred keyword membership."""

from typing import Literal

from parent_child_pharmacology.clients import mprint_data
from parent_child_pharmacology.core.population import preserve_population
from parent_child_pharmacology.models.contracts import (
    PMID,
    EvidenceResponse,
    Limit20,
    Offset,
    OptionalQuery,
)
from parent_child_pharmacology.models.inputs import Population

UPDATE_PROCESS = (
    "The server is read-only, so a question never rewrites the saved copy. When newer MPRINT data exists, a "
    "maintainer rebuilds the snapshot and updates mprint-manifest.json; a weekly automated check also flags "
    "new releases. Until then, answers keep using the dated saved copy and say so."
)


async def find_mprint_records(
    drug: OptionalQuery = "",
    pmid: PMID | None = None,
    population: Population = "any",
    study_type: Literal["any", "PK", "PE", "CT", "PD", "PG", "RCT"] = "any",
    max_results: Limit20 = 10,
    resolve_names: bool = True,
    offset: Offset = 0,
    include_classifications: bool = False,
    check_for_updates: bool = False,
) -> EvidenceResponse:
    """Find curated Gold study metadata by drug or exact PMID; one selector is required,
    unless check_for_updates is true. When a user asks whether MPRINT data is current, up to date
    or has newer releases, call with check_for_updates=true (drug optional): the server checks the
    MPRINT repository live and reports whether newer data exists than the saved copy.
    If both supplied, both must match. Follow with get_mprint_details for outcomes.
    Snapshot inclusion is not proof of safety, quality, or MPRINT funding.
    Follow next_offset for complete cohorts. include_classifications joins automated Silver
    labels and exported outcome counts for all returned PMIDs; these are not clinical findings.
    Age-band requests preserve the requested band; broad source labels are not age-band confirmation.
    Results come from a dated saved copy: show data_freshness.display_note with any MPRINT answer."""
    upstream = None
    if check_for_updates:
        from parent_child_pharmacology.core.freshness import check_upstream, mprint_freshness

        upstream = await check_upstream()
        if not drug and not pmid:
            return {
                "source": "local:mprint-snapshot",
                "data_freshness": mprint_freshness(),
                "upstream_check": upstream,
                "update_process": UPDATE_PROCESS,
            }
    if not drug and not pmid:
        return {"source": "validation", "error": "selector_required"}
    broad = (
        "pediatric" if population in {"neonate", "infant", "child", "adolescent"} else population
    )
    out = await mprint_data.search_gold(
        drug, max_results, broad, study_type, resolve_names, pmid, offset, include_classifications
    )
    if upstream is not None:
        out = {**out, "upstream_check": upstream, "update_process": UPDATE_PROCESS}
    return preserve_population(out, population)


async def get_mprint_details(
    pmid: PMID,
    table: Literal[
        "gold_outcomes", "gold_PE_CT", "gold_PK_summary", "silver_classifications"
    ] = "gold_outcomes",
    max_results: Limit20 = 5,
    offset: Offset = 0,
) -> EvidenceResponse:
    """Get aggregate curated Gold outcomes OR automated Silver classifications by PMID.
    Select table explicitly; Silver labels are not curated Gold clinical findings.
    Gold null means missing in exported data, not zero. Context joins are by PMID and workbook,
    not cohort or treatment arm; do not assign every outcome to every drug. Doses are source
    observations, never recommendations. No individual-patient data. Preserve snapshot provenance.
    Silver returns the single-PMID classification lookup; max_results/offset apply to Gold only.
    Results come from a dated saved copy: show data_freshness.display_note with any MPRINT answer."""
    if table == "silver_classifications":
        out = await mprint_data.silver_classifications([pmid])
    else:
        kind = {"gold_outcomes": "any", "gold_PE_CT": "PE_CT", "gold_PK_summary": "PK_summary"}[
            table
        ]
        out = await mprint_data.gold_outcomes(pmid, kind, max_results, offset)
    return {**out, "requested_table": table, "pmid": pmid}
