"""Agent-facing literature actions."""
import asyncio
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urlencode
from typing import Literal
from core import config as cfg, safety as parent_safety
from clients import lakehouse as lh, pediatric_labels, mprint_data, nichd, parent_resources as parents
import clients as src
from models.contracts import *
from .common import _lakehouse_or_none
from models.inputs import Population
log = logging.getLogger('mc')

async def search_literature(query: Query, population: Population = "any", max_results: Limit20 = 10,
                            mode: Literal["auto", "semantic", "keyword"] = "auto",
                            focus: Literal['all','maternal','exposure','offspring_outcomes','maternal_pharmacokinetics'] = 'all') -> EvidenceResponse:
    """Search PubMed literature. Pregnancy/lactation always use curated, versioned MeSH plus title/abstract strategies, optional focus, and no date restriction. Pass a medicine name, not PubMed syntax. For other populations, 'keyword' hits live PubMed;
    'semantic' uses the lakehouse vector index of maternal/child abstracts; 'auto' prefers semantic.
    Use a concise query (drug plus one concept), not a whole question. If empty, simplify
    without dropping the drug. Check relevance and call get_abstracts before describing
    study findings. Empty results do not establish absence of evidence."""
    from core.literature_strategy import strategy
    curated=strategy(query,population,focus)
    max_results = max(1, min(max_results, 20))
    if not curated and mode != "keyword" and cfg.USE_LAKEHOUSE:
        q = query if population == "any" else f"{query} ({population})"
        try:
            rows = await lh.vector(cfg.index("pubmed_idx"), q, ["pmid", "title", "journal", "year"], max_results)
            if rows:
                return {"source": "lakehouse:vector", "results": [
                    {**r, "url": f"https://pubmed.ncbi.nlm.nih.gov/{r['pmid']}/"} for r in rows]}
        except Exception as e:
            log.warning("vector search failed (%s)", type(e).__name__)
    params={'focus':focus} if focus!='all' else {}
    results=await src.pubmed_search(query, population, max_results,**params)
    return {"source": "live:pubmed", "url": src.pubmed_search_url(query, population, max_results,**params),
            "query": query, "population": population, "publication_date_lookback_years": None if curated else 10,
            "query_strategy":curated, "search_metadata":getattr(results,'search_metadata',{}), "results":list(results)}

async def get_abstracts(pmids: PMIDs10) -> EvidenceResponse:
    """Get abstracts and canonical PubMed source URLs for up to 10 PubMed IDs.
    Cite each article's returned URL. No returned article is a retrieval limitation,
    not evidence that a paper or research does not exist."""
    if not pmids or any(not re.fullmatch(r"[1-9][0-9]{0,9}", p) for p in pmids):
        return {"source": "validation", "error": "invalid_pmids",
                "note": "Pass numeric PMID strings returned by search_literature, not drug names, URLs or mixed text.",
                "url": "https://pubmed.ncbi.nlm.nih.gov/"}
    return {"source": "live:pubmed", "articles": await src.pubmed_abstracts(pmids)}

async def search_trials(condition_or_drug: Query, population: Population = "pregnancy",
                        max_results: Limit20 = 10) -> EvidenceResponse:
    """Research landscape across trial statuses, including historical studies.
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
    return {"source": "live:clinicaltrials.gov",
            "studies": await src.trials_search(condition_or_drug, population, max(1, min(max_results, 20)))}

async def search_funded_research(topic: Query, max_results: Limit25 = 10) -> EvidenceResponse:
    """Search NIH RePORTER for funded projects (newest first) on a maternal/child topic.
    For NICHD program staff: portfolio oversight, topic discovery and links to public awards;
    no assessment of grant performance, private records, or funding recommendations.
    Use title and abstract to assess relevance; omit indirect matches from the main
    answer. A funded project is not a completed finding or proof of MPRINT membership."""
    return {"source": "live:reporter", "projects": await src.reporter_search(topic, max(1, min(max_results, 25)))}
