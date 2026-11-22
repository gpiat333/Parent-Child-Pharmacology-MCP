from importlib import import_module


def register_prompts(mcp):
    for name in [
        "breastfeeding_medication_check",
        "pregnancy_medication_check",
        "clinician_literature_scan",
        "questions_to_ask_clinician",
    ]:
        import_module(__name__ + "." + name).register(mcp)
