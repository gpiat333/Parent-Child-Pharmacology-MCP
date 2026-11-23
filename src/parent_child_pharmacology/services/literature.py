"""Agent-facing literature actions."""

import logging
import re
from typing import Literal

import parent_child_pharmacology.clients as src
from parent_child_pharmacology.clients import (
    lakehouse as lh,
)
from parent_child_pharmacology.core import config as cfg
from parent_child_pharmacology.models.contracts import (
    EvidenceResponse,
    Limit20,
    Limit25,
    OptionalQuery,
    PMIDs10,
    Query,
)
from parent_child_pharmacology.models.inputs import (
    IC,
    NCTID,
    ActivityCode,
    FiscalYears,
    ISODate,
    Population,
    PublicationType,
)

log = logging.getLogger("mc")


async def search_literature(
    query: Query,
    population: Population = "any",
    max_results: Limit20 = 10,
    mode: Literal["auto", "semantic", "keyword"] = "auto",
    focus: Literal[
        "all", "maternal", "exposure", "offspring_outcomes", "maternal_pharmacokinetics"
    ] = "all",
    publication_type: PublicationType = "any",
    date_from: ISODate | None = None,
    date_to: ISODate | None = None,
    offset: int = 0,
) -> EvidenceResponse:
    """Search PubMed literature. Pregnancy/lactation use curated, versioned MeSH strategies with optional focus; no default date restriction. publication_type maps a small enum to PubMed types; date_from/date_to are inclusive publication-date bounds. These filters force live PubMed. Results retain source publication types, PMC IDs and availability-derived free/full-text fields; an ID alone is not proof of access. Pass a medicine name, not PubMed syntax. For other populations, 'keyword' hits live PubMed;
    'semantic' uses the lakehouse vector index of maternal/child abstracts; 'auto' prefers semantic.
    Use a concise query (drug plus one concept), not a whole question. If empty, simplify
    without dropping the drug. Check relevance and call get_abstracts before describing
    study findings. Empty results do not establish absence of evidence."""
    from parent_child_pharmacology.core.literature_strategy import strategy

    curated = strategy(query, population, focus)
    max_results = max(1, min(max_results, 20))
    filtered = publication_type != "any" or date_from or date_to or offset
    if not curated and not filtered and mode != "keyword" and cfg.USE_LAKEHOUSE:
        q = query if population == "any" else f"{query} ({population})"
        try:
            rows = await lh.vector(
                cfg.index("pubmed_idx"), q, ["pmid", "title", "journal", "year"], max_results
            )
            if rows:
                return {
                    "source": "lakehouse:vector",
                    "results": [
                        {**r, "url": f"https://pubmed.ncbi.nlm.nih.gov/{r['pmid']}/"} for r in rows
                    ],
                }
        except Exception as e:
            log.warning("vector search failed (%s)", type(e).__name__)
    params = {"focus": focus} if focus != "all" else {}
    if offset:
        params["offset"] = offset
        max_results = min(max_results, 10000 - offset)
    if publication_type != "any":
        params["publication_type"] = publication_type
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    results = await src.pubmed_search(query, population, max_results, **params)
    return {
        "source": "live:pubmed",
        "url": src.pubmed_search_url(query, population, max_results, **params),
        "query": query,
        "population": population,
        "publication_date_lookback_years": None if curated or date_from or date_to else 10,
        "applied_filters": {
            "publication_type": publication_type,
            "date_from": date_from,
            "date_to": date_to,
        },
        "query_strategy": curated,
        "search_metadata": getattr(results, "search_metadata", {}),
        "results": list(results),
    }


async def get_abstracts(pmids: PMIDs10) -> EvidenceResponse:
    """Get abstracts and canonical PubMed source URLs for up to 10 PubMed IDs.
    Cite each article's returned URL. No returned article is a retrieval limitation,
    not evidence that a paper or research does not exist. Preserve abstract_coverage
    and required_display_notices when records lack abstract text or were not returned;
    titles and metadata alone do not establish study outcomes."""
    if not pmids or any(not re.fullmatch(r"[1-9][0-9]{0,9}", p) for p in pmids):
        return {
            "source": "validation",
            "error": "invalid_pmids",
            "note": "Pass numeric PMID strings returned by search_literature, not drug names, URLs or mixed text.",
            "url": "https://pubmed.ncbi.nlm.nih.gov/",
        }
    from parent_child_pharmacology.core.abstract_coverage import coverage

    try:
        articles = await src.pubmed_abstracts(pmids)
    except Exception:
        return {
            "source": "live:pubmed",
            "articles": [],
            "error": "abstract_retrieval_failed",
            "abstract_coverage": coverage(pmids, [], request_failed=True),
            "note": "Abstract retrieval failed; abstract availability is unknown.",
        }
    articles = [
        {
            **a,
            "abstract_status": "retrieved"
            if isinstance(a.get("abstract"), str) and a["abstract"].strip()
            else "no_text_returned",
        }
        for a in articles
    ]
    return {
        "source": "live:pubmed",
        "articles": articles,
        "abstract_coverage": coverage(pmids, articles),
    }


async def search_trials(
    condition_or_drug: OptionalQuery = "",
    population: Population = "pregnancy",
    max_results: Limit20 = 10,
    nct_id: NCTID | None = None,
) -> EvidenceResponse:
    """Research landscape across trial statuses, including historical studies. Supply nct_id alone for a direct single-record fetch. Each record includes exact status and results_posted/has_results; completed does not mean results posted, and neither establishes benefit.
    For joining a study, location, contacts or current enrollment, prefer
    find_recruiting_studies. Search ClinicalTrials.gov for pregnancy, lactation or pediatrics.
    Use returned conditions, interventions and summaries to assess relevance. Omit
    indirect matches from the main answer; registration/status is not evidence of benefit.
    When asked to omit dose numbers, use intervention name_without_strength.
    It is display formatting, not normalized ingredient identity; original name is retained.
    Link EVERY listed study using its returned study URL and state its exact status.
    For current/ongoing studies, separate RECRUITING, ENROLLING_BY_INVITATION and
    ACTIVE_NOT_RECRUITING from NOT_YET_RECRUITING, historical/closed and UNKNOWN.
    ACTIVE_NOT_RECRUITING does not mean open enrollment. Never place completed or
    unknown-status studies in the ongoing list. State when no relevant ongoing study
    was returned; do not imply the search was exhaustive."""
    if nct_id:
        return {
            "source": "live:clinicaltrials.gov",
            "lookup_method": "direct_nct_id",
            "studies": [await src.trial_by_nct(nct_id, population)],
        }
    return {
        "source": "live:clinicaltrials.gov",
        "studies": await src.trials_search(
            condition_or_drug, population, max(1, min(max_results, 20))
        ),
    }


async def search_funded_research(
    topic: Query,
    max_results: Limit25 = 10,
    ic: IC = "any",
    fiscal_years: FiscalYears | None = None,
    activity_code: ActivityCode = "",
    organization: OptionalQuery = "",
) -> EvidenceResponse:
    """Search NIH RePORTER for funded projects (newest first) on a maternal/child topic. Optional IC enum (HD maps to NICHD), fiscal_years, exact activity_code and organization-name filters become reproducible query_criteria. Fiscal-year award obligations and direct costs remain separate; neither is lifetime project value.
    For NICHD program staff: portfolio oversight, topic discovery and links to public awards;
    no assessment of grant performance, private records, or funding recommendations.
    Use title and abstract to assess relevance; omit indirect matches from the main
    answer. A funded project is not a completed finding or proof of MPRINT membership."""
    filters = {
        k: v
        for k, v in {
            "ic": ic,
            "fiscal_years": fiscal_years,
            "activity_code": activity_code,
            "organization": organization,
        }.items()
        if v and v != "any"
    }
    rows = await src.reporter_search(topic, max_results, **filters)
    return {
        "source": "live:reporter",
        "projects": list(rows),
        "search_metadata": getattr(rows, "search_metadata", {}),
        "query_criteria": getattr(rows, "search_metadata", {}).get("criteria"),
        "amount_notice": "Fiscal-year obligations in USD, not lifetime project value. Total award and direct costs are separate.",
        "funder_scope": "NIH RePORTER only. Other funders such as FDA, CDC, PCORI, foundations and industry are not included; say so when answering who funds a topic.",
    }


async def summarize_research_portfolio(
    drug_or_topic: Query,
    ic: IC = "any",
    fiscal_years: FiscalYears | None = None,
    activity_code: ActivityCode = "",
    organization: OptionalQuery = "",
    max_projects: int = 200,
) -> EvidenceResponse:
    """Aggregate a bounded public RePORTER portfolio by administering IC and fiscal year. Return exact query criteria, counts, separate total-award/direct-cost sums and missing amounts. HD means NICHD. Subprojects are excluded. These are fiscal-year obligations, not lifetime project value or proof of performance; check complete_result_set before describing totals as complete."""
    from parent_child_pharmacology.clients.reporter import research_portfolio

    out = await research_portfolio(
        drug_or_topic, ic, fiscal_years, activity_code, organization, max_projects
    )
    if isinstance(out, dict):
        out.setdefault(
            "funder_scope",
            "NIH RePORTER only. Other funders such as FDA, CDC, PCORI, foundations and industry are not included; say so when answering who funds a topic.",
        )
    return out
