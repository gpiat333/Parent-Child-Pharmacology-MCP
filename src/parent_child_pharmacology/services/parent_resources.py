"""Agent-facing parent_resources actions."""

import logging
from typing import Literal

from parent_child_pharmacology.clients import (
    parent_resources as parents,
)
from parent_child_pharmacology.core import safety as parent_safety
from parent_child_pharmacology.models.contracts import (
    Country,
    EvidenceResponse,
    Limit20,
    OptionalQuery,
    Query,
    Question,
)
from parent_child_pharmacology.models.inputs import Population

log = logging.getLogger("mc")


async def route_parent_question(question: Question, country: Country = "US") -> EvidenceResponse:
    """Call FIRST for parent-facing requests, before evidence retrieval. Returns fixed
    referral/urgent/identity/privacy guidance and allow_research. If false, show the
    message with source URLs and stop research. Rule-based prototype, NOT validated
    clinical triage. Country is explicit; never invent a local emergency number.
    On an allowed request, enforce requested_workflow.required_tool when present:
    call that tool before other retrieval or a final answer. All stop rules take priority.
    If personal_question is true ("Can I take X?"), research is allowed: share what the
    sources say and what is unknown, show the message and referrals, and never answer yes
    or no or call it safe for this person.
    Do not include names, contact details, birth dates or medical record numbers."""
    if len(question) > 4000:
        return {
            "source": "validation",
            "allow_research": False,
            "message": "Use a short question without an identifiable health history.",
        }
    return parent_safety.route(question, country)


async def get_parent_medication_info(drug: Query) -> EvidenceResponse:
    """Preferred for parent questions about side effects and breastfeeding infant findings.
    Use this focused bundle, not medication_evidence_brief, when papers/trials/FAERS
    are not requested. Parent-facing evidence bundle after confirming drug identity. Separates label
    adverse effects in the medicine taker, LactMed infant evidence, and MedlinePlus
    education links. Monitoring recommendations are not observed infant effects.
    Follow source limitations; never diagnose symptoms or give personal medication
    decisions, doses, schedules, missed-dose or taper instructions."""
    return await parents.medication_info(drug)


async def search_medication_recalls(
    drug: Query,
    manufacturer: OptionalQuery = "",
    lot: OptionalQuery = "",
    max_results: Limit20 = 10,
) -> EvidenceResponse:
    """FDA drug enforcement recall candidates, including historical records. Show
    each returned candidate with manufacturer, product/formulation text, lots, dates,
    exact status, reason and official link, including when the supplied lot does not match.
    A total count alone omits returned candidate details. A literal
    lot mention is NOT confirmation; ranges and all-lot notices need verification.
    Never clear a bottle from absent/different lot results. Consumer instructions
    may be missing: refer to official notice/pharmacist, never invent them."""
    return await parents.recalls(drug, manufacturer, lot, max_results)


async def search_drug_safety_alerts(
    drug: OptionalQuery = "", max_results: Limit20 = 10
) -> EvidenceResponse:
    """Search titles on the current FDA Drug Safety Communications index. Returns
    dates and official notice links, not full notices, personal advice or all archives.
    No match does not establish safety; use exact brand/generic words separately."""
    return await parents.safety_alerts(drug, max_results)


async def find_recruiting_studies(
    topic: Query,
    population: Population = "any",
    location: OptionalQuery = "",
    max_results: Limit20 = 10,
) -> EvidenceResponse:
    """Preferred for participation questions ("can I join a study?"). Use search_trials
    for a research landscape across statuses, not enrollment discovery.
    Discover potentially relevant RECRUITING studies and public eligibility,
    contacts, site status, locations and update dates. Location is city/state/country,
    not home address. Not an eligibility decision or enrollment. Overall recruitment
    does not mean every site recruits; study team must confirm current availability.
    Use population='pediatric' for children: only records with pediatric age metadata
    are listed; adult-only and unverified-age records are withheld. If none remain,
    lead with no verified pediatric match in this bounded search, not broader studies."""
    return await parents.recruiting_studies(topic, population, location, max_results)


async def search_pregnancy_registries(
    drug: OptionalQuery = "", max_results: Limit20 = 10
) -> EvidenceResponse:
    """FDA-listed pregnancy exposure registries: medicine/condition, registry, public
    contacts, source status and links. FDA does not run or endorse them; list is not
    comprehensive. Verify enrollment with registry. No eligibility or safety claim."""
    return await parents.pregnancy_registries(drug, max_results)


async def find_pregnancy_exposure_registries(drug: Query) -> EvidenceResponse:
    """Participation tier: find FDA-directory pregnancy exposure registries for a confirmed
    medicine. Returns directory source, contacts, links and source status. FDA does not
    run or endorse these registries. No ranking, recommendation, eligibility decision
    or contact. Call question preflight first; suppress on urgent/crisis/identity stops.
    An empty match is a bounded directory result, not proof no registry exists."""
    from parent_child_pharmacology.core.participation import tier

    return tier(await parents.pregnancy_registries(drug, 20))


async def search_parent_input_opportunities(
    topic: Query, agency: Literal["NIH", "FDA"] = "NIH", max_results: Limit20 = 10
) -> EvidenceResponse:
    """Discover NIH/FDA Federal Register notices plus public-engagement directories.
    Use a concise subject such as 'clinical research' or 'pregnancy', not a whole
    question or extra words such as 'parent public input'. If empty, simplify the
    subject while preserving the research topic; do not invent opportunities.
    Candidates may be RFIs, comment requests or meetings; verify title/text, audience,
    official deadline and submission instructions. Use comment_deadline.date and
    relation_to_as_of to group dates, separately from submission_status and relevance.
    A known future date is not an unknown date even if submission acceptance is
    unverified. Meeting dates never establish comment deadlines or closure.
    Unknown comment deadline is neither verified open nor verified closed.
    Coverage is incomplete. Never submit comments or collect personal histories."""
    return await parents.input_opportunities(topic, agency, max_results)


async def get_reporting_resources() -> EvidenceResponse:
    """Official navigation links for FDA MedWatch and NIH/FDA public involvement.
    No report/comment submitted. Reporting does not prove causation or replace urgent
    care. Do not collect identifiable medical details in this MCP."""
    return parents.reporting_resources()
