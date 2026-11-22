"""Explicit agent-facing input contracts. Names and fields are stable protocol API."""
from typing import Literal
from pydantic import Field, ConfigDict, model_validator
from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase
from .contracts import *
Population = Literal['pregnancy','lactation','neonate','infant','child','adolescent','pediatric','any']
class StrictInput(ArgModelBase):
    model_config = ConfigDict(extra='forbid',strict=True)


class RouteParentQuestionInput(StrictInput):
    question: Question = Field(..., description='Question.', examples=['What lactation evidence is available for sertraline?'])
    country: Country = Field('US', description='Country.', examples=['US'])


class GetParentMedicationInfoInput(StrictInput):
    drug: Query = Field(..., description='Drug.', examples=['sertraline'])


class SearchMedicationRecallsInput(StrictInput):
    drug: Query = Field(..., description='Drug.', examples=['sertraline'])
    manufacturer: OptionalQuery = Field('', description='Manufacturer.', examples=['Example manufacturer'])
    lot: OptionalQuery = Field('', description='Lot.', examples=['ABC123'])
    max_results: Limit20 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class SearchDrugSafetyAlertsInput(StrictInput):
    drug: OptionalQuery = Field('', description='Drug.', examples=['sertraline'])
    max_results: Limit20 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class FindRecruitingStudiesInput(StrictInput):
    topic: Query = Field(..., description='Topic.', examples=['pediatric epilepsy'])
    population: Population = Field('any', description='Population.', examples=['lactation'])
    location: OptionalQuery = Field('', description='Location.', examples=['Maryland'])
    max_results: Limit20 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class SearchPregnancyRegistriesInput(StrictInput):
    drug: OptionalQuery = Field('', description='Drug.', examples=['sertraline'])
    max_results: Limit20 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])

class FindPregnancyExposureRegistriesInput(StrictInput):
    drug: Query = Field(...,description='Confirmed medicine name. FDA directory navigation, not a recommendation.')


class SearchParentInputOpportunitiesInput(StrictInput):
    topic: Query = Field(..., description='Topic.', examples=['pediatric epilepsy'])
    agency: Literal['NIH', 'FDA'] = Field('NIH', description='Agency.', examples=['NIH'])
    max_results: Limit20 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class GetReportingResourcesInput(StrictInput):
    pass


class NormalizeDrugInput(StrictInput):
    name: Query = Field(..., description='Name.', examples=['Zoloft'])


class SearchLactmedInput(StrictInput):
    drug: Query = Field(..., description='Drug.', examples=['sertraline'])
    max_results: Limit20 = Field(5, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class GetLactmedRecordInput(StrictInput):
    book_id: BookID = Field(..., description='Numeric LactMed record ID returned by search_lactmed.', examples=['4569784'])
    max_chars: TextLimit = Field(6000, description='Max chars.', examples=[6000])


class SemanticSearchLactmedInput(StrictInput):
    question: Question = Field(..., description='Question.', examples=['What lactation evidence is available for sertraline?'])
    max_results: Limit20 = Field(5, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class SearchLiteratureInput(StrictInput):
    query: Query = Field(..., description='Query.', examples=['levetiracetam breastfeeding'])
    population: Population = Field('any', description='Population.', examples=['lactation'])
    max_results: Limit20 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])
    mode: Literal['auto', 'semantic', 'keyword'] = Field('auto', description='Mode.', examples=['keyword'])
    focus: Literal['all','maternal','exposure','offspring_outcomes','maternal_pharmacokinetics'] = Field('all', description='Curated MeSH focus for pregnancy or lactation. These populations use live PubMed and no date restriction.')


class GetAbstractsInput(StrictInput):
    pmids: PMIDs10 = Field(..., description='Nonempty list of numeric PubMed identifiers from source records.', examples=[['38841362']])


class GetLabelSectionsInput(StrictInput):
    drug: Query = Field(..., description='Drug.', examples=['sertraline'])


class SearchPediatricLabelingChangesInput(StrictInput):
    drug: Query = Field(..., description='Drug.', examples=['sertraline'])
    legislation: Literal['any', 'BPCA', 'PREA'] = Field('any', description='Legislation.', examples=['BPCA'])
    max_results: Limit20 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class SearchTrialsInput(StrictInput):
    condition_or_drug: Query = Field(..., description='Condition or drug.', examples=['pediatric epilepsy'])
    population: Population = Field('pregnancy', description='Population.', examples=['lactation'])
    max_results: Limit20 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class SearchFundedResearchInput(StrictInput):
    topic: Query = Field(..., description='Topic.', examples=['pediatric epilepsy'])
    max_results: Limit25 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class FindMprintRecordsInput(StrictInput):
    drug: OptionalQuery = Field('', description='Exact drug name, or omit when using PMID.')
    pmid: PMID | None = Field(None, description='Exact PubMed ID. Drug or PMID is required.')
    population: Population = 'any'
    study_type: Literal['any','PK','PE','CT','PD','PG','RCT'] = 'any'
    max_results: Limit20 = 10
    resolve_names: bool = True

    @model_validator(mode='after')
    def require_selector(self):
        if not self.drug and not self.pmid: raise ValueError('Provide drug or pmid')
        return self

class GetMprintDetailsInput(StrictInput):
    pmid: PMID
    table: Literal['gold_outcomes','gold_PE_CT','gold_PK_summary','silver_classifications'] = 'gold_outcomes'
    max_results: Limit20 = 5
    offset: Offset = 0


class GetAdverseEventSignalsInput(StrictInput):
    drug: Query = Field(..., description='Drug.', examples=['sertraline'])
    cohort: Literal['any', 'pregnancy', 'infant'] = Field('any', description='Cohort.', examples=['infant'])
    max_results: Limit25 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class GetPatientEducationInput(StrictInput):
    language: Literal['en','es'] = Field('en', description='Spanish drug links require a confirmed RxNorm ID; no Spanish free-text search.')
    topic: Query = Field(..., description='Topic.', examples=['pediatric epilepsy'])
    rxcui: RxCUI | None = Field(None, description='Exact numeric RxNorm concept identifier; not a medicine name.', examples=['36437'])


class SearchBpcaEvidenceInput(StrictInput):
    query: OptionalQuery = Field('', description='Query.', examples=['levetiracetam breastfeeding'])
    max_results: Limit25 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])


class SearchNichdStudiesInput(StrictInput):
    query: OptionalQuery = Field('', description='Query.', examples=['levetiracetam breastfeeding'])
    network: Literal['any', 'mfmu', 'neonatal'] = Field('any', description='Network.', examples=['mfmu'])
    max_results: Limit25 = Field(10, description='Maximum returned records; the schema defines valid bounds.', examples=[5])
    page: Page = Field(0, description='Page.', examples=[0])


class MedicationEvidenceBriefInput(StrictInput):
    drug: Query = Field(..., description='Drug.', examples=['sertraline'])
    population: Literal['pregnancy', 'lactation', 'neonate', 'infant', 'child', 'adolescent', 'pediatric'] = Field('lactation', description='Population.', examples=['lactation'])

INPUT_MODELS = {
    'route_parent_question': RouteParentQuestionInput,
    'get_parent_medication_info': GetParentMedicationInfoInput,
    'search_medication_recalls': SearchMedicationRecallsInput,
    'search_drug_safety_alerts': SearchDrugSafetyAlertsInput,
    'find_recruiting_studies': FindRecruitingStudiesInput,
    'search_pregnancy_registries': SearchPregnancyRegistriesInput,
    'find_pregnancy_exposure_registries': FindPregnancyExposureRegistriesInput,
    'search_parent_input_opportunities': SearchParentInputOpportunitiesInput,
    'get_reporting_resources': GetReportingResourcesInput,
    'normalize_drug': NormalizeDrugInput,
    'search_lactmed': SearchLactmedInput,
    'get_lactmed_record': GetLactmedRecordInput,
    'semantic_search_lactmed': SemanticSearchLactmedInput,
    'search_literature': SearchLiteratureInput,
    'get_abstracts': GetAbstractsInput,
    'get_label_sections': GetLabelSectionsInput,
    'search_pediatric_labeling_changes': SearchPediatricLabelingChangesInput,
    'search_trials': SearchTrialsInput,
    'search_funded_research': SearchFundedResearchInput,
    'find_mprint_records': FindMprintRecordsInput,
    'get_mprint_details': GetMprintDetailsInput,
    'get_adverse_event_signals': GetAdverseEventSignalsInput,
    'get_patient_education': GetPatientEducationInput,
    'search_bpca_evidence': SearchBpcaEvidenceInput,
    'search_nichd_studies': SearchNichdStudiesInput,
    'medication_evidence_brief': MedicationEvidenceBriefInput,
}
