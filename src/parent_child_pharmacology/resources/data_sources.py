from parent_child_pharmacology.core import config as cfg


def register(mcp):
    @mcp.resource("mother-child://sources")
    def data_sources() -> str:

        return (
            "Sources: LactMed (lactation only) and PubMed (NCBI E-utilities), DailyMed and RxNorm (NLM), MedlinePlus (NLM), "
            "NICHD BPCA/PTN summary index, NICHD DASH public study metadata (controlled data excluded), ClinicalTrials.gov (NLM), NIH RePORTER, openFDA FAERS, FDA pediatric labeling changes workbook. Program-staff portfolio discovery is supported via "
            "RePORTER/PubMed; two Gold/Silver snapshot tools query versioned published data subsets. "
            "Parent navigation also uses openFDA enforcement recalls, FDA safety communications and pregnancy registry directories, "
            "ClinicalTrials.gov participation fields and official MedWatch/NIH/FDA links. "
            "Parent clients must call route_parent_question and enforce safety fields; these rules are not clinically validated triage. "
            + cfg.DISCLAIMER
        )
