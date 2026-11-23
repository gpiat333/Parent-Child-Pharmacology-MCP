"""Fixed, verified referral text. Numbers are never model-generated or paraphrased.

Verified 2026-11-22 against the providers' own pages:
- MotherToBaby (OTIS): https://mothertobaby.org/contact/ and /ask-an-expert
- PRGLAC: https://www.nichd.nih.gov/about/advisory/council/PRGLAC-implementation-WG-of-council
"""

MOTHERTOBABY = {
    "name": "MotherToBaby (Organization of Teratology Information Specialists)",
    "call": "866-626-6847",
    "phone_link": "tel:18666266847",
    "website": "https://mothertobaby.org/ask-an-expert",
    "hours": "Specialists respond Monday to Friday, 8 am to 7 pm ET; after hours, by the next business day.",
    "role": "Free, individualized information about medicines and other exposures during pregnancy and breastfeeding, "
    "for US residents. A nonprofit service, not a federal source, and not an emergency or crisis line.",
}

MOTHERTOBABY_MESSAGE = (
    "For a question about your own pregnancy or breastfeeding, MotherToBaby specialists can talk it "
    "through with you for free: call 866-626-6847 or visit mothertobaby.org (weekdays 8 am to 7 pm ET)."
)

PRGLAC_CONTEXT = {
    "framework": "PRGLAC: Task Force on Research Specific to Pregnant Women and Lactating Women",
    "summary": "Created by the 21st Century Cures Act (2016). Its September 2018 report to the HHS Secretary "
    "made 15 recommendations to close research gaps on safe and effective therapies in pregnancy and "
    "lactation. An implementation plan followed in August 2020, and an NICHD Council working group has "
    "tracked implementation since 2023.",
    "why_shown": "Empty or thin pregnancy and lactation evidence rows are a known, national research gap, "
    "not a finding that a medicine is safe or unsafe.",
    "links": [
        "https://www.nichd.nih.gov/about/advisory/council/PRGLAC-implementation-WG-of-council",
        "https://www.nichd.nih.gov/sites/default/files/inline-files/PRGLAC_Implement_Plan_083120.pdf",
    ],
}
