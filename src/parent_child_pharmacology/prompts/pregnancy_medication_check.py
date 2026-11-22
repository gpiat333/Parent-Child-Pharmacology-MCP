def register(mcp):
    @mcp.prompt()
    def pregnancy_medication_check(drug: str) -> str:

        return (
            f"First call route_parent_question on the parent's actual question and honor allow_research=false. "
            f"Someone who is pregnant asks about {drug}. If research is allowed, call medication_evidence_brief with "
            "population='pregnancy'. Show maternal effects, measured fetal/infant exposure and observed fetal/infant outcomes as three rows, keeping empty rows. Include maternal pharmacokinetics and source-only dose-adjustment context, with explicit gaps. Show participation separately, unranked and never recommended. Explain the label's pregnancy section and key literature in plain "
            "language, note uncertainty and limits of the evidence, cite sources, and recommend "
            "discussing with their prenatal care provider. Do not give a personalized yes/no decision "
            "about continuing, stopping or starting, a dose, or a taper schedule. If evidence is "
            "missing, acknowledge the gap instead of adding uncited medical claims."
        )
