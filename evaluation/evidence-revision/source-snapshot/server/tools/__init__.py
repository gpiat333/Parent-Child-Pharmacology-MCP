"""Register stable tools, named input models and protocol annotations."""
import inspect
from importlib import import_module
from mcp.types import ToolAnnotations
from core.audit import audited
from models.inputs import INPUT_MODELS
DOMAINS = {'identity': ['normalize_drug'], 'lactation': ['search_lactmed', 'get_lactmed_record', 'semantic_search_lactmed'], 'literature': ['search_literature', 'get_abstracts', 'search_trials', 'search_funded_research'], 'labels_safety': ['get_label_sections', 'search_pediatric_labeling_changes', 'get_adverse_event_signals', 'get_patient_education'], 'mprint': ['find_mprint_records', 'get_mprint_details'], 'nichd': ['search_bpca_evidence', 'search_nichd_studies'], 'parent_resources': ['route_parent_question', 'get_parent_medication_info', 'search_medication_recalls', 'search_drug_safety_alerts', 'find_recruiting_studies', 'search_pregnancy_registries', 'find_pregnancy_exposure_registries', 'search_parent_input_opportunities', 'get_reporting_resources'], 'composite': ['medication_evidence_brief']}

def register(mcp):
    exported={}
    for domain,names in DOMAINS.items():
        module=import_module('tools.'+domain)
        for name in names:
            fn=getattr(module,name)
            from .descriptions import description
            wrapped=audited(fn)
            wrapped.__doc__=description(name, fn.__doc__, domain)
            mcp.add_tool(wrapped,structured_output=True,annotations=ToolAnnotations(readOnlyHint=True,destructiveHint=False,idempotentHint=True,openWorldHint=True))
            registered=mcp._tool_manager.get_tool(name)
            registered.fn_metadata.arg_model=INPUT_MODELS[name]
            registered.parameters=INPUT_MODELS[name].model_json_schema(by_alias=True)
            exported[name]=wrapped
    from .resources import register as resources
    resources(mcp)
    return exported
