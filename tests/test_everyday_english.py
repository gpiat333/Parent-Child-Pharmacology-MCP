"""Everyday English requests must pass the language check; other languages must still stop."""

import pytest

from parent_child_pharmacology.core.safety import route

EVERYDAY_ENGLISH = [
    "What does LactMed say about sertraline and breastfeeding? Link the studies.",
    "What does the MotherToBaby fact sheet say about sertraline in pregnancy?",
    "Find the Spanish MotherToBaby fact sheet on acetaminophen.",
    "Give me an evidence brief on sertraline in pregnancy.",
    "I'm breastfeeding. Can I take ibuprofen?",
    "What does research say about lamotrigine for seizures in pregnancy?",
    "Give me an evidence brief for lamotrigine in a child.",
    "Where has metformin been studied in adults? Is it used off-label in children?",
    "Is the MPRINT data current?",
    "What NIH funding is there on sertraline in pregnancy?",
    "Give me a pregnancy evidence brief for sertraline. What are the PRGLAC recommendations?",
    "Summarize the evidence on amoxicillin in breastfed infants. Include links.",
    "Compare the label warnings for metformin with LactMed findings. Cite sources.",
    "Show me recruiting studies for ADHD in children. Include study links.",
    "List FDA recalls for naproxen.",
    "Search PubMed for levetiracetam during breastfeeding.",
    "Tell me about ondansetron in pregnancy. Keep it short.",
    "Check the evidence coverage for daridorexant in pregnancy.",
    "Is there a pregnancy registry for topiramate? Give me the contact.",
    "What are the side effects of Zoloft for my baby?",
    "How much sertraline gets into breast milk?",
    "Are there studies on ADHD medication during pregnancy? Please link them.",
    "Explain what LactMed says about sumatriptan. Separate measured levels from infant outcomes.",
    "My toddler takes amoxicillin. What do studies show?",
    "Look up the FDA label for Tylenol. What does it say about pregnancy?",
    "Find NICHD-funded research on neonatal pharmacology in 2025.",
    "Get the abstract for PMID 22077504.",
    "Use LactMed. What about fluoxetine?",
    "Thanks! Now do the same for escitalopram.",
    "And what about ibuprofen?",
    "Can you check the MotherToBaby fact sheet for ondansetron?",
    "I'm pregnant and take levothyroxine. What does the research say?",
    "Does Benadryl pass into breast milk?",
    "Is acetaminophen OK while nursing?",
    "Describe pediatric labeling changes for montelukast.",
    "Provide FDA safety communications about montelukast with links.",
]


@pytest.mark.parametrize("question", EVERYDAY_ENGLISH)
def test_everyday_english_is_not_language_blocked(question):
    assert route(question)["route"] != "language_support"


@pytest.mark.parametrize(
    "question",
    [
        "¿Puedo tomar ibuprofeno durante el embarazo?",
        "Puis-je prendre du paracétamol pendant la grossesse?",
        "Kann ich Ibuprofen in der Schwangerschaft nehmen?",
        "Posso tomar ibuprofeno durante a gravidez?",
        "Estoy embarazada. Can I take ibuprofen?",
        "Link the studies sobre sertralina durante la lactancia.",
        "Thanks! Ahora haga lo mismo para escitalopram.",
    ],
)
def test_other_and_mixed_languages_still_stop(question):
    assert route(question)["allow_research"] is False


def test_landing_page_explains_the_app():
    from starlette.testclient import TestClient

    from parent_child_pharmacology.app import mcp

    page = TestClient(mcp.streamable_http_app()).get("/")
    assert page.status_code == 200 and "This is an MCP server" in page.text
