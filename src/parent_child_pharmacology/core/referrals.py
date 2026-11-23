"""Fixed, verified referral text. Numbers are never model-generated or paraphrased.

Verified 2026-11-22 against the providers' own pages:
- MotherToBaby (OTIS): https://mothertobaby.org/contact/ and /ask-an-expert
- PRGLAC: https://www.nichd.nih.gov/about/advisory/council/PRGLAC-implementation-WG-of-council
Verified 2026-11-23:
- PRGLAC recommendations: https://www.nichd.nih.gov/about/advisory/PRGLAC/recommendations
- BPCA priority list: https://www.nichd.nih.gov/research/supported/bpca/recent-priority-lists
- MotherToBaby in Spanish: https://mothertobaby.org/es/ ("¡Hablamos español!" on /contact/)
- 988 in Spanish: https://988lifeline.org/es/servicios-de-traduccion/servicios-en-espanol/
- MedlinePlus en español: https://medlineplus.gov/spanish/druginformation.html
- NCCIH Herbs at a Glance: https://www.nccih.nih.gov/health/herbsataglance
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
        "https://www.nichd.nih.gov/about/advisory/PRGLAC/recommendations",
        "https://www.nichd.nih.gov/about/advisory/council/PRGLAC-implementation-WG-of-council",
        "https://www.nichd.nih.gov/sites/default/files/inline-files/PRGLAC_Implement_Plan_083120.pdf",
    ],
    "recommendations_source": "https://www.nichd.nih.gov/about/advisory/PRGLAC/recommendations",
    "recommendations_note": "The 15 recommendation headings from the September 2018 PRGLAC report, as listed by NICHD. "
    "Numbers 14 and 15 are shortened; see the source for full wording and sub-recommendations.",
    "recommendations": [
        "1. Include and integrate pregnant women and lactating women in the clinical research agenda",
        "2. Increase the quantity, quality, and timeliness of research on safety and efficacy of therapeutic "
        "products used by pregnant women and lactating women",
        "3. Expand the workforce of clinicians and research investigators with expertise in obstetric and "
        "lactation pharmacology and therapeutics",
        "4. Remove regulatory barriers to research in pregnant women",
        "5. Create a public awareness campaign to engage the public and health care providers in research on "
        "pregnant women and lactating women",
        "6. Develop and implement evidence-based communication strategies with health care providers on "
        "information relevant to research on pregnant women and lactating women",
        "7. Reduce liability to facilitate an evidence base for new therapeutic products that may be used by "
        "women who are, or may become, pregnant and by lactating women",
        "8. Develop separate programs to study therapeutic products used off-patent in pregnant women and "
        "lactating women using the NIH BPCA as a model",
        "9. Develop programs to drive discovery and development of therapeutics and new therapeutic products "
        "for conditions specific to pregnant women and lactating women",
        "10. Implement a proactive approach to protocol development and study design to include pregnant women "
        "and lactating women in clinical research",
        "11. Leverage established and support new infrastructures/collaborations to perform research in "
        "pregnant women and lactating women",
        "12. Utilize and improve existing resources for data to inform the evidence and provide a foundation "
        "for research on pregnant women and lactating women",
        "13. Optimize registries for pregnancy and lactation",
        "14. The HHS Secretary should consider extending the Task Force (extended March 13, 2019 to March 13, 2021)",
        "15. Establish an Advisory Committee to monitor and report on implementation of recommendations (deferred)",
    ],
}


OFF_LABEL_CONTEXT = {
    "what_off_label_means": "A use not listed in a product's FDA-approved label, such as a medicine approved for "
    "adults that is prescribed for a child. Off-label use is common in children and is legal, but it is not "
    "recorded in the label, so no single public database lists every off-label use.",
    "where_to_look": [
        {
            "source": "FDA label: indications and clinical studies",
            "what": "What the product is approved for and the studies behind the approval, mostly in adults "
            "(get_label_sections, approved_use_sections).",
        },
        {
            "source": "FDA label: pediatric use, and FDA pediatric labeling changes",
            "what": "Whether and for which ages children's use has been studied and labeled "
            "(get_label_sections, search_pediatric_labeling_changes).",
        },
        {
            "source": "NICHD BPCA Priority List of Needs in Pediatric Therapeutics",
            "what": "Off-patent medicines NICHD has prioritized for pediatric study because children's evidence "
            "or labeling is lacking.",
            "url": "https://www.nichd.nih.gov/research/supported/bpca/recent-priority-lists",
        },
        {
            "source": "Published studies in adults or children",
            "what": "search_literature with population any (adults included) or a pediatric population.",
        },
    ],
    "not_a_recommendation": "Being studied or approved in adults does not establish a dose, safety or "
    "effectiveness in children. A child's prescriber decides about off-label use.",
}

SPANISH_RESOURCES = {
    "note": "Questions in Spanish are not answered automatically because the safety rules are English-only. "
    "These Spanish-language services and the server's Spanish tools are available.",
    "referrals": [
        {
            "name": "MotherToBaby (Spanish service)",
            "call": "866-626-6847",
            "website": "https://mothertobaby.org/es/",
            "role": "Free information about medicines in pregnancy and breastfeeding; specialists speak "
            "Spanish. Weekdays 8 am to 7 pm ET.",
        },
        {
            "name": "988 Suicide & Crisis Lifeline in Spanish",
            "call": "988, then press 2",
            "text": "AYUDA to 988",
            "website": "https://988lifeline.org/es/servicios-de-traduccion/servicios-en-espanol/",
            "role": "Free crisis support in Spanish, 24 hours a day.",
        },
        {
            "name": "MedlinePlus en español: medicines, herbs and supplements",
            "website": "https://medlineplus.gov/spanish/druginformation.html",
            "role": "NIH consumer drug information in Spanish.",
        },
    ],
    "spanish_tools": [
        "search_mothertobaby_fact_sheets with language es: MotherToBaby fact sheets in Spanish, verbatim.",
        "get_patient_education with a confirmed medicine: MedlinePlus education, including Spanish where available.",
    ],
}

SUPPLEMENT_CONTEXT = {
    "note": "Herbs, supplements and essential oils are often not FDA-approved medicines, so they may have no "
    "FDA label and little research. LactMed covers many herbs and supplements during breastfeeding.",
    "links": ["https://www.nccih.nih.gov/health/herbsataglance"],
}
