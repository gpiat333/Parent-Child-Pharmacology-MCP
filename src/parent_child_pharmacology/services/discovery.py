"""Bounded source coverage and identity navigation, after mandatory preflight."""

from typing import Literal

from parent_child_pharmacology.models.contracts import (
    EvidenceResponse,
    Limit20,
    OptionalQuery,
    Query,
)
from parent_child_pharmacology.models.inputs import Population


async def check_evidence_coverage(drug: Query, population: Population) -> EvidenceResponse:
    """Count-only source-presence/gap navigation before full evidence retrieval. Probe PubMed, trial registrations, lactation-only LactMed, labels and MPRINT row counts, with snapshot dates and caveats. No abstracts or clinical payloads. Counts cannot establish evidence quality or safety; unavailable is not zero. This is not clinical triage. Preflight the actual question first."""
    from parent_child_pharmacology.clients.coverage import evidence_coverage

    return await evidence_coverage(drug, population)


async def find_products_containing_ingredient(
    ingredient: Query, max_results: Limit20 = 20
) -> EvidenceResponse:
    """Find RxNorm branded/clinical products containing one confirmed ingredient to help recognize possible duplicate-ingredient exposure across products used for children. Identity information only, not a dose calculation, dosing/safety check, substitution recommendation or verification of the package in hand. Confirm the ingredient first; lists are bounded and alphabetical."""
    from parent_child_pharmacology.clients.rxnorm import products_containing_ingredient

    return await products_containing_ingredient(ingredient, max_results)


async def search_drug_shortages(
    drug: Query,
    dosage_form: OptionalQuery = "",
    status: Literal["any", "Current", "Resolved", "Discontinued"] = "any",
    max_results: Limit20 = 10,
) -> EvidenceResponse:
    """Search FDA's public drug-shortage records by medicine and optional dosage form/status. Preserve presentation, availability and update dates: Current shortage status can include an Available presentation. No local pharmacy-stock, pediatric suitability, substitution, dosing or safety inference."""
    from parent_child_pharmacology.clients.shortages import search_shortages

    return await search_shortages(drug, dosage_form, status, max_results)
