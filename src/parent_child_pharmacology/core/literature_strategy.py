"""Versioned, inspectable MeSH strategies; no raw PubMed query-language passthrough."""

import re

VERSION = "2026-11-20.1"
POPULATIONS = {
    "pregnancy": '("Pregnancy"[MeSH Terms] OR pregnan*[Title/Abstract] OR gestation*[Title/Abstract])',
    "lactation": '("Lactation"[MeSH Terms] OR "Breast Feeding"[MeSH Terms] OR "Milk, Human"[MeSH Terms] OR lactat*[Title/Abstract] OR breastfeed*[Title/Abstract] OR breastfed[Title/Abstract])',
}
FOCI = {
    "maternal": '("Maternal Health"[MeSH Terms] OR "Treatment Outcome"[MeSH Terms] OR maternal[Title/Abstract] OR mother*[Title/Abstract] OR "milk production"[Title/Abstract])',
    "exposure": '("Placenta"[MeSH Terms] OR "Milk, Human"[MeSH Terms] OR "Fetal Blood"[MeSH Terms] OR "Drug Levels"[Title/Abstract] OR concentration*[Title/Abstract] OR transfer[Title/Abstract] OR exposure[Title/Abstract])',
    "offspring_outcomes": '("Pregnancy Outcome"[MeSH Terms] OR "Infant, Newborn"[MeSH Terms] OR "Congenital Abnormalities"[MeSH Terms] OR outcome*[Title/Abstract] OR neonat*[Title/Abstract] OR infant*[Title/Abstract])',
    "maternal_pharmacokinetics": '("Pharmacokinetics"[MeSH Terms] OR "Drug Elimination Routes"[MeSH Terms] OR pharmacokinetic*[Title/Abstract] OR clearance[Title/Abstract] OR "area under the curve"[Title/Abstract] OR "dose adjustment"[Title/Abstract])',
}
STOP = set(
    "evidence pregnancy pregnant lactation breastfeeding breastfed maternal fetal infant infants during for in on of the and research study studies outcomes outcome exposure pharmacokinetics pharmacokinetic brief summary".split()
)


def strategy(query, population, focus="all"):
    if population not in POPULATIONS:
        return None
    if focus != "all" and focus not in FOCI:
        raise ValueError("Unknown literature focus")
    # Field every medicine/topic token. User-supplied operators/brackets cannot
    # override population or focus. Preserve the chosen terms in query provenance.
    terms = list(
        dict.fromkeys(
            t.lower()
            for t in re.findall(r"[A-Za-z][A-Za-z0-9-]*", query)
            if t.lower() not in STOP and t.upper() not in {"OR", "NOT", "AND"}
        )
    )
    if not terms:
        raise ValueError("Provide the medicine name with the population separately")
    concept = " AND ".join(
        f'("{t}"[MeSH Terms] OR "{t}"[Substance Name] OR "{t}"[Title/Abstract])' for t in terms
    )
    full = f"({concept}) AND {POPULATIONS[population]}"
    if focus != "all":
        full += " AND " + FOCI[focus]
    return {
        "version": VERSION,
        "population": population,
        "focus": focus,
        "concept_terms": terms,
        "pubmed_query": full,
        "date_restriction": None,
        "human_filter": False,
        "limitations": [
            "Curated prototype query strategy, not a validated systematic-review search.",
            "MeSH plus title/abstract terms includes unindexed recent records. Drug synonyms and imperfect indexing can still be missed.",
            "Animal, in vitro, modeling and human records may be returned. Preserve study type; never call predicted exposure measured human exposure.",
        ],
    }
