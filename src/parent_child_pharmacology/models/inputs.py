"""Explicit agent-facing input contracts. Names and fields are stable protocol API."""

from typing import Annotated, Literal

from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase
from pydantic import ConfigDict, Field, model_validator

from parent_child_pharmacology.core.research_filters import IC, PublicationType

from .contracts import (
    PMID,
    BookID,
    Country,
    Limit20,
    Limit25,
    Offset,
    OptionalQuery,
    Page,
    PMIDs10,
    Query,
    Question,
    RxCUI,
    TextLimit,
)

FiscalYears = Annotated[
    list[Annotated[int, Field(ge=1985, le=2100)]], Field(min_length=1, max_length=20)
]
ActivityCode = Annotated[str, Field(pattern=r"^(?:[A-Z][A-Z0-9]{2})?$", max_length=3)]
ISODate = Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
NCTID = Annotated[str, Field(pattern=r"^NCT[0-9]{8}$")]
Population = Literal[
    "pregnancy", "lactation", "neonate", "infant", "child", "adolescent", "pediatric", "any"
]


class StrictInput(ArgModelBase):
    model_config = ConfigDict(extra="forbid", strict=True)
    response_format: Literal["json", "markdown"] = Field(
        "json",
        description="Text display format. Both formats retain the full typed structuredContent and safety notices.",
    )


class RouteParentQuestionInput(StrictInput):
    question: Question = Field(
        ...,
        description="The user's question in their own words, without names or other identifiers.",
        examples=["What lactation evidence is available for sertraline?"],
    )
    country: Country = Field(
        "US",
        description="Country the user is in; used only to choose emergency contacts.",
        examples=["US"],
    )


class NormalizeDrugInput(StrictInput):
    name: Query = Field(
        ...,
        description="Brand, generic or misspelled medicine name to resolve.",
        examples=["Zoloft"],
    )


class SearchLiteratureInput(StrictInput):
    offset: Annotated[int, Field(ge=0, le=9999)] = Field(
        0,
        description="PubMed retstart offset from pagination.next_offset. Nonzero offsets use live PubMed; PubMed limits retrieval to the first 10,000 hits.",
    )
    query: Query = Field(
        ...,
        description="Medicine name plus at most one concept; not a whole question or PubMed syntax.",
        examples=["levetiracetam breastfeeding"],
    )
    population: Population = Field(
        "any",
        description="Who the evidence should be about. Age bands: neonate under 28 days, infant to under 2 years, child 2 to 11, adolescent 12 to 17.",
        examples=["lactation"],
    )
    max_results: Limit20 = Field(
        10, description="Maximum records returned; see minimum and maximum.", examples=[5]
    )
    mode: Literal["auto", "semantic", "keyword"] = Field(
        "auto",
        description="auto prefers semantic search when a vector index is configured; keyword always uses live PubMed.",
        examples=["keyword"],
    )
    focus: Literal[
        "all", "maternal", "exposure", "offspring_outcomes", "maternal_pharmacokinetics"
    ] = Field(
        "all",
        description="Curated MeSH focus for pregnancy or lactation. Live PubMed; no default date restriction unless date_from/date_to are supplied.",
    )
    publication_type: PublicationType = Field(
        "any", description="Limit to one PubMed publication type; forces live PubMed."
    )
    date_from: ISODate | None = Field(
        None, description="Earliest publication date, YYYY-MM-DD, inclusive."
    )
    date_to: ISODate | None = Field(
        None, description="Latest publication date, YYYY-MM-DD, inclusive."
    )

    @model_validator(mode="after")
    def dates(self):
        from datetime import date

        for v in [self.date_from, self.date_to]:
            if v:
                date.fromisoformat(v)
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must not follow date_to")
        return self


class GetAbstractsInput(StrictInput):
    pmids: PMIDs10 = Field(
        ...,
        description="Nonempty list of numeric PubMed identifiers from source records.",
        examples=[["38841362"]],
    )


class GetLabelSectionsInput(StrictInput):
    drug: Query = Field(
        ...,
        description="Generic or brand name of one medicine, for example sertraline or Zoloft.",
        examples=["sertraline"],
    )


class SearchPediatricLabelingChangesInput(StrictInput):
    drug: Query = Field(
        ...,
        description="Generic or brand name of one medicine, for example sertraline or Zoloft.",
        examples=["sertraline"],
    )
    legislation: Literal["any", "BPCA", "PREA"] = Field(
        "any", description="Filter by the law behind the labeling change.", examples=["BPCA"]
    )
    max_results: Limit20 = Field(
        10, description="Maximum records returned; see minimum and maximum.", examples=[5]
    )


class SearchTrialsInput(StrictInput):
    condition_or_drug: OptionalQuery = Field(
        "",
        description="Condition or medicine; omit when fetching by nct_id.",
        examples=["pediatric epilepsy"],
    )
    population: Population = Field(
        "any",
        description="Limit studies to pregnancy, lactation or a pediatric age band. The default, "
        "any, applies no population filter.",
        examples=["lactation"],
    )
    max_results: Limit20 = Field(10, description="Maximum studies returned (1-20).", examples=[5])
    nct_id: NCTID | None = Field(
        None, description="Exact NCT identifier for a direct record fetch, without a search."
    )
    recruiting_only: bool = Field(
        False,
        description="true for studies recruiting now, with eligibility, contacts and sites, as an "
        "unranked participation listing. false for the research landscape across all statuses.",
    )
    location: OptionalQuery = Field(
        "",
        description="recruiting_only: city, state or country to filter study sites; never a "
        "home address.",
        examples=["Maryland"],
    )

    @model_validator(mode="after")
    def selector(self):
        if bool(self.condition_or_drug) == bool(self.nct_id):
            raise ValueError("Provide exactly one of condition_or_drug or nct_id")
        if self.recruiting_only and self.nct_id:
            raise ValueError("recruiting_only needs condition_or_drug, not nct_id")
        if self.location and not self.recruiting_only:
            raise ValueError("location applies only when recruiting_only is true")
        return self


class SearchFundedResearchInput(StrictInput):
    topic: Query = Field(
        ...,
        description="Research topic; for a medicine, add a population, for example sertraline pregnancy.",
        examples=["pediatric epilepsy"],
    )
    max_results: Limit25 = Field(
        10, description="Maximum records returned; see minimum and maximum.", examples=[5]
    )
    ic: IC = Field(
        "any",
        description="Administering NIH IC code; HD maps to NICHD in the RePORTER agency filter.",
    )
    fiscal_years: FiscalYears | None = Field(
        None, description="NIH fiscal years to include, for example [2024, 2025]."
    )
    activity_code: ActivityCode = Field(
        "",
        description="Exact three-character NIH activity code, e.g. R01, R21, K12; not a wildcard series.",
    )
    organization: OptionalQuery = Field("", description="Upstream organization-name partial match.")


class SummarizeResearchPortfolioInput(StrictInput):
    drug_or_topic: Query = Field(
        ...,
        description="Research topic or medicine; for a medicine, add a population.",
        examples=["neonatal pharmacology"],
    )
    ic: IC = Field("any", description="Administering NIH institute code; HD is NICHD.")
    fiscal_years: FiscalYears | None = Field(
        None, description="NIH fiscal years to include, for example [2024, 2025]."
    )
    activity_code: ActivityCode = Field(
        "", description="Exact three-character NIH activity code such as R01; not a series."
    )
    organization: OptionalQuery = Field("", description="Organization name, partial match.")
    max_projects: Annotated[int, Field(ge=1, le=500)] = Field(
        200, description="Most project records to retrieve and aggregate (1-500)."
    )


class CheckEvidenceCoverageInput(StrictInput):
    drug: Query = Field(
        ..., description="Generic or brand name of one medicine.", examples=["levetiracetam"]
    )
    population: Population = Field(
        ..., description="Who the evidence should be about.", examples=["pregnancy"]
    )


class FindProductsContainingIngredientInput(StrictInput):
    ingredient: Query = Field(
        ...,
        description="One confirmed active ingredient, not a brand or combination product.",
        examples=["acetaminophen"],
    )
    max_results: Limit20 = Field(20, description="Maximum products returned (1-20).")


class FindMprintRecordsInput(StrictInput):
    drug: OptionalQuery = Field("", description="Exact drug name, or omit when using PMID.")
    pmid: PMID | None = Field(None, description="Exact PubMed ID. Drug or PMID is required.")
    population: Population = Field("any", description="Limit to studies in one population.")
    study_type: Literal["any", "PK", "PE", "CT", "PD", "PG", "RCT"] = Field(
        "any",
        description="PK pharmacokinetics, PE pharmacoepidemiology, CT clinical trial, PD "
        "pharmacodynamics, PG pharmacogenetics, RCT randomized controlled trial.",
    )
    max_results: Limit20 = Field(10, description="Maximum records returned (1-20).")
    resolve_names: bool = Field(
        True, description="Also match the generic ingredient when a brand name is given."
    )
    offset: Offset = Field(0, description="Row offset from pagination.next_offset.")
    include_classifications: bool = Field(
        False,
        description="Join automated Silver labels and exported outcome counts for each returned PMID. Not clinical findings.",
    )
    check_for_updates: bool = Field(
        False,
        description="Check live whether MPRINT has published newer data than the saved copy. Use when asked if MPRINT data is current.",
    )

    @model_validator(mode="after")
    def require_selector(self):
        if not self.drug and not self.pmid and not self.check_for_updates:
            raise ValueError("Provide drug or pmid, or set check_for_updates")
        return self


class GetMprintDetailsInput(StrictInput):
    pmid: PMID = Field(..., description="PubMed ID of a study returned by find_mprint_records.")
    table: Literal["gold_outcomes", "gold_PE_CT", "gold_PK_summary", "silver_classifications"] = (
        Field(
            "gold_outcomes",
            description="gold_outcomes: all curated outcome rows. gold_PE_CT: pharmacoepidemiology "
            "and trial outcomes. gold_PK_summary: pharmacokinetic summaries. "
            "silver_classifications: automated study-type labels, not curated findings.",
        )
    )
    max_results: Limit20 = Field(5, description="Maximum outcome rows returned (1-20).")
    offset: Offset = Field(0, description="Row offset from pagination.next_offset.")


class GetAdverseEventSignalsInput(StrictInput):
    drug: Query = Field(
        ...,
        description="Generic or brand name of one medicine, for example sertraline or Zoloft.",
        examples=["sertraline"],
    )
    cohort: Literal["any", "pregnancy", "infant"] = Field(
        "any",
        description="Limit FAERS reports to pregnancy-exposure reports or to infants aged 0 to 12 months.",
        examples=["infant"],
    )
    max_results: Limit25 = Field(
        10, description="Maximum records returned; see minimum and maximum.", examples=[5]
    )


class GetPatientEducationInput(StrictInput):
    language: Literal["en", "es"] = Field(
        "en",
        description="Spanish drug links require a confirmed RxNorm ID; no Spanish free-text search.",
    )
    topic: Query = Field(
        ...,
        description="Health topic or medicine name in English.",
        examples=["pediatric epilepsy"],
    )
    rxcui: RxCUI | None = Field(
        None,
        description="Exact numeric RxNorm concept identifier; not a medicine name.",
        examples=["36437"],
    )


class MedicationEvidenceBriefInput(StrictInput):
    drug: Query = Field(
        ...,
        description="Generic or brand name of one medicine, for example sertraline or Zoloft.",
        examples=["sertraline"],
    )
    population: Literal[
        "pregnancy", "lactation", "neonate", "infant", "child", "adolescent", "pediatric"
    ] = Field(
        "lactation",
        description="Who the evidence should be about. Age bands: neonate under 28 days, infant to under 2 years, child 2 to 11, adolescent 12 to 17.",
        examples=["lactation"],
    )
    detail: Literal["summary", "full"] = Field(
        "summary",
        description="summary: every evidence axis with totals, the first passages per list and "
        "compact source records. full: every passage and the source text; very large.",
    )


class SearchMothertobabyFactSheetsInput(StrictInput):
    drug: Query = Field(..., description="Medicine or exposure name.", examples=["sertraline"])
    language: Literal["any", "en", "es"] = Field("any", description="Fact sheet language.")
    max_results: Limit20 = Field(5, description="Maximum fact sheets returned (1-20).")
    include_text: bool = Field(True, description="Return verbatim question-and-answer text.")
    max_chars: TextLimit = Field(8000, description="Total text budget; whole answers only.")


class SearchFdaDrugNoticesInput(StrictInput):
    kind: Literal["recalls", "safety_communications", "shortages", "reporting_links"] = Field(
        ...,
        description="Which FDA notices to look up: recalls, safety_communications, shortages, or "
        "reporting_links for MedWatch and public-involvement links.",
        examples=["recalls"],
    )
    drug: OptionalQuery = Field(
        "",
        description="Generic or brand name. Required for recalls and shortages; optional for "
        "safety_communications; unused for reporting_links.",
        examples=["sertraline"],
    )
    manufacturer: OptionalQuery = Field(
        "", description="Recalls only: manufacturer name as printed on the package."
    )
    lot: OptionalQuery = Field(
        "", description="Recalls only: lot number as printed on the package.", examples=["ABC123"]
    )
    dosage_form: OptionalQuery = Field(
        "", description="Shortages only: dosage form such as tablet or injection."
    )
    status: Literal["any", "Current", "Resolved", "Discontinued"] = Field(
        "any", description="Shortages only: FDA shortage status filter."
    )
    max_results: Limit20 = Field(10, description="Maximum records returned (1-20).")

    @model_validator(mode="after")
    def drug_when_needed(self):
        if self.kind in {"recalls", "shortages"} and not self.drug:
            raise ValueError("drug is required for recalls and shortages")
        return self


class FindPregnancyExposureRegistriesInput(StrictInput):
    drug: OptionalQuery = Field(
        "",
        description="Confirmed medicine name; omit to list the FDA directory. Navigation only, "
        "not a recommendation.",
        examples=["topiramate"],
    )
    max_results: Limit20 = Field(20, description="Maximum registries returned (1-20).")


class GetLactmedRecordInput(StrictInput):
    drug: OptionalQuery = Field(
        "",
        description="Medicine or vaccine name, generic preferred. Finds and reads the record in "
        "one call.",
        examples=["sertraline"],
    )
    book_id: BookID | None = Field(
        None,
        description="Numeric LactMed record id from an earlier result, used to pick one of several "
        "candidate records. Not an NBK accession or a drug name.",
        examples=["4573436"],
    )
    max_chars: TextLimit = Field(
        16000, description="Maximum characters of record text (500-20000).", examples=[16000]
    )

    @model_validator(mode="after")
    def selector(self):
        if not self.drug and not self.book_id:
            raise ValueError("Provide drug or book_id")
        return self


class SearchNichdResourcesInput(StrictInput):
    query: OptionalQuery = Field(
        "",
        description="Drug, condition or title words; empty lists the index.",
        examples=["levetiracetam"],
    )
    source: Literal["bpca_summaries", "dash_studies"] = Field(
        "bpca_summaries",
        description="bpca_summaries: BPCA and Pediatric Trials Network study-summary links. "
        "dash_studies: public NICHD DASH study descriptions and publications.",
    )
    network: Literal["any", "mfmu", "neonatal"] = Field(
        "any", description="dash_studies only: limit to one NICHD research network."
    )
    max_results: Limit25 = Field(10, description="Maximum records returned (1-25).")
    page: Page = Field(0, description="dash_studies only: zero-based result page (0-100).")


INPUT_MODELS = {
    "search_mothertobaby_fact_sheets": SearchMothertobabyFactSheetsInput,
    "route_parent_question": RouteParentQuestionInput,
    "search_fda_drug_notices": SearchFdaDrugNoticesInput,
    "search_nichd_resources": SearchNichdResourcesInput,
    "find_pregnancy_exposure_registries": FindPregnancyExposureRegistriesInput,
    "normalize_drug": NormalizeDrugInput,
    "get_lactmed_record": GetLactmedRecordInput,
    "search_literature": SearchLiteratureInput,
    "get_abstracts": GetAbstractsInput,
    "get_label_sections": GetLabelSectionsInput,
    "search_pediatric_labeling_changes": SearchPediatricLabelingChangesInput,
    "search_trials": SearchTrialsInput,
    "search_funded_research": SearchFundedResearchInput,
    "find_mprint_records": FindMprintRecordsInput,
    "get_mprint_details": GetMprintDetailsInput,
    "get_adverse_event_signals": GetAdverseEventSignalsInput,
    "get_patient_education": GetPatientEducationInput,
    "medication_evidence_brief": MedicationEvidenceBriefInput,
    "summarize_research_portfolio": SummarizeResearchPortfolioInput,
    "check_evidence_coverage": CheckEvidenceCoverageInput,
    "find_products_containing_ingredient": FindProductsContainingIngredientInput,
}
