"""Typed results for the most-used tools, on top of the shared evidence envelope.

Each model names the fields a client can rely on for that tool. Every tool-specific field is
optional, because a safety stop, an identity stop or a source failure returns the envelope
without them. Source records keep any extra fields their source provides.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, model_serializer

from .contracts import EvidenceResponse


class SourceRecord(BaseModel):
    """One record from a source; unlisted source fields are preserved."""

    model_config = ConfigDict(extra="allow")


class ToolResponse(EvidenceResponse):
    """Envelope plus tool-specific fields; fields a result did not set are left out."""

    @model_serializer(mode="wrap")
    def _omit_unset_tool_fields(self, handler):
        data = handler(self)
        envelope = EvidenceResponse.model_fields
        for name in type(self).model_fields:
            if name not in envelope and name not in self.model_fields_set:
                data.pop(name, None)
        return data


class RouteResponse(ToolResponse):
    route: str | None = None
    allow_research: bool | None = None
    message: str | None = None
    message_es: str | None = None
    referrals: list[dict[str, Any]] | None = None
    personal_question: bool | None = None
    requested_workflow: dict[str, Any] | None = None
    language_gate: dict[str, Any] | None = None


class NormalizeDrugResponse(ToolResponse):
    found: bool | None = None
    input: str | None = None
    rxcui: str | None = None
    matched_name: str | None = None
    term_type: str | None = None
    ingredients: list[str] | None = None
    match_type: str | None = None
    requires_confirmation: bool | None = None


class LactmedRecordResponse(ToolResponse):
    book_id: str | int | None = None
    title: str | None = None
    url: str | None = None
    text: str | None = None
    sections: dict[str, str] | None = None
    sections_missing: list[str] | None = None
    truncated: bool | None = None
    exposure_measurements: dict[str, Any] | None = None
    references: list[dict[str, Any]] | None = None
    record_revised_on: str | None = None
    data_freshness: dict[str, Any] | None = None
    requires_record_selection: bool | None = None
    matched_record: dict[str, Any] | None = None


class Citation(SourceRecord):
    pmid: str | int | None = None
    title: str | None = None
    journal: str | None = None
    year: str | int | None = None
    url: str | None = None


class LiteratureResponse(ToolResponse):
    query: str | None = None
    population: str | None = None
    results: list[Citation] = []
    pagination: dict[str, Any] | None = None


class Article(Citation):
    abstract: str | None = None
    abstract_status: str | None = None


class AbstractsResponse(ToolResponse):
    articles: list[Article] | None = None


class Study(SourceRecord):
    nct: str | None = None
    title: str | None = None
    status: str | None = None
    results_posted: bool | None = None
    url: str | None = None


class TrialsResponse(ToolResponse):
    search_mode: str | None = None
    studies: list[Study] | None = None


class AxisPassages(SourceRecord):
    ingredient: str | None = None
    axis: str | None = None
    state: str | None = None
    items: list[dict[str, Any]] = []
    context_only: list[dict[str, Any]] = []
    reported_gaps: list[dict[str, Any]] = []
    report_only_context: list[dict[str, Any]] = []


class EvidenceAxis(SourceRecord):
    axis: str
    label: str | None = None
    by_ingredient: list[AxisPassages] = []


class BriefResponse(ToolResponse):
    detail: str | None = None
    drug_input: str | None = None
    population: str | None = None
    queried_ingredients: list[str] | None = None
    evidence_axes: list[EvidenceAxis] | None = None
    ingredient_evidence: list[dict[str, Any]] | None = None
    questions_to_ask_clinician: list[str] | None = None
    citations: list[str] | None = None
    requires_confirmation: bool | None = None


OUTPUT_MODELS = {
    "route_parent_question": RouteResponse,
    "normalize_drug": NormalizeDrugResponse,
    "get_lactmed_record": LactmedRecordResponse,
    "search_literature": LiteratureResponse,
    "get_abstracts": AbstractsResponse,
    "search_trials": TrialsResponse,
    "medication_evidence_brief": BriefResponse,
}
