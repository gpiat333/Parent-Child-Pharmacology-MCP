def register(mcp):
    @mcp.prompt()
    def breastfeeding_medication_check(drug: str) -> str:

        return (
            f"First call route_parent_question on the parent's actual question and honor allow_research=false. "
            f"A breastfeeding parent asks about taking {drug}. If research is allowed, call medication_evidence_brief with "
            f"population='lactation'. Summarize in plain language: what LactMed says about milk transfer "
            "and infant outcomes, maternal effects and label statements. Show all three evidence axes even if empty, and "
            "keep source recommendations separate from observed outcomes. Cite sources and discuss questions with their clinician "
            "or pharmacist. Do not give dosing or tell them to stop or start a medication."
        )
