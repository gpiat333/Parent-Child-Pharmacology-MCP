# MCP design audit — 20 November 2026

## Follow-up: fixes deployed

The initial findings below are retained as the pre-fix audit. They no longer
describe all current contract behavior. Deployment `01f1e53dd5881e4b8ed6111cd924fc14`
adds `mc/contracts.py`: strict input types, rejection of extra arguments, bounded
strings/numbers/lists, identifier patterns, and a typed common response envelope.
Names/defaults are retained; accepted inputs are intentionally narrower. Empty
discovery searches remain allowed where documented. Source-specific output fields
remain extensible and are not individually modeled.

Results: **250 unit tests passed**, including **35 new contract tests**;
**36/36 deployed contract checks** and **21/21 deployed source/safety checks** passed.
`post-fix-results.json` retains the same 15 validation probes separately from the
original `results.json`; negative limits, empty required inputs, unknown fields,
numeric strings and malformed IDs are now rejected before retrieval.

Tool descriptions now distinguish parent information vs broad research briefs,
and study participation vs research across trial statuses. Combination-product
and infant-only FAERS scope limitations are explicit in the composite description.

Two fresh chat-selection probes were attempted but **blocked before model output**:
the Databricks route `models.ai.gpt-5-6-luna` returned HTTP 401 with
`expired_secret_key`. No new chat-selection success or MLflow score is claimed.
Synthetic traces: `presentation-evidence/contract-parent-20261120-results.json`
and `contract-enrollment-20261120-results.json` in the companion project.
The workspace route's provider credential requires administrator renewal.

The historical notes below describe the initial audit and remain for comparison.

Scope: inspect the local registered FastMCP tools and exercise the same argument-validation path with a capture callback replacing retrieval. No live data calls, deployment, or new MLflow experiment. Production code was not changed.

## Verified

- 27/27 registered tools have generated Pydantic BaseModel argument classes (MCP 1.30.0; Pydantic 2.14.3). Explicit handwritten BaseModel classes are not required for this generation.
- Literal choices become JSON Schema enums. Invalid population, network and agency values are rejected before function execution.
- Missing required strings, wrong string/list-item types, and noninteger text limits are rejected.
- `functools.wraps` in `mc/audit.py` preserves the signature used by FastMCP.
- Existing unit suite rerun: **215 passed in 4.06 seconds**.
- `audit.py` saves all 15 characterization probes and schemas to `results.json`. These probes document behavior; they are not 15 clinical accuracy tests.

## Contract gaps

- All 27 tool output schemas are null; responses are generic dictionaries. Safety/provenance fields are populated by application code, not validated by a declared response model.
- Numeric bounds are absent from the inspected input schemas. For example, `search_lactmed` accepts -1 and 9999 at schema validation and then clamps to 1–20 in the function.
- Empty drug strings and empty PMID lists pass schema validation. Record ID format is checked inside the function rather than declared as a schema pattern.
- Unexpected fields are ignored; numeric string `"5"` is coerced to integer 5. Strict rejection should be a deliberate compatibility decision.
- Recommend Annotated/Field bounds and descriptions, nonempty identifier/list constraints, and typed response envelopes. Distinguish intentional empty searches (some discovery tools) from missing required identity. Test changed contracts before deployment; do not present these recommendations as already implemented.

## Tool design assessment

Strong goal-level tools: `get_parent_medication_info` separates parent label effects, infant evidence and education; `find_recruiting_studies` applies recruitment/population checks and returns contacts/site status; `medication_safety_brief` resolves identity and gathers multiple sources with partial-failure handling.

Focused retrieval tools remain useful building blocks: LactMed search → record retrieval and PubMed search → abstract retrieval. Descriptions specify prerequisites and limits. Do not claim that every tool independently orchestrates multiple APIs.

Selection risks: broad `medication_safety_brief` overlaps parent information; `search_trials` overlaps recruiting-study discovery. Clarify preferred workflow, output scope and applicability in tool descriptions and test realistic agent selection. `semantic_search_lactmed` is advertised but unavailable without configured vector infrastructure. MPRINT inferred discovery must remain distinct from curated snapshot lookup.

Composite caveats observed in code: combination products query only the first ingredient and return a warning; pediatric briefs map FAERS to an infant cohort, which is narrower than all pediatrics. This scope should be explicit in the composite result and description. These were code-review findings, not new live behavior tests.

The router is a separate tool, not universal clinical-policy enforcement at the protocol boundary. Privacy checks are shared; personal-treatment boundaries also depend on the chat client's preflight and handling. Prompt instructions alone cannot guarantee third-party client compliance.

## Evaluation evidence for presentation

- Broader set: `evaluation/parent-generalization/full-run.json`, run `4075650d4a3c4e1ebd4e253719fc009f`: 16 questions (12 research, 4 boundary), tool selection/boundary/citation provenance 16/16 each, fidelity 14/16, task fulfillment 10/16.
- Targeted unchanged follow-up: `evaluation/population-deadline-final/full-run.json`, run `20bb013dde97463d9fc63d3def41678a`: 5 cases, 25/25 assessments. Only 3 research answers use AI judgments; 2 refusals use fixed contracts. This is not a new broad benchmark.
- Calibration: evidence fidelity 4/4 controls; task fulfillment 3/4, diagnostic only. Do not claim clinical certification or general accuracy.
- Prior deployed checks: 21/21. Research chat durations in the three-case follow-up: 19.557, 15.771, 27.309 seconds (end-to-end, not server-only latency). No load benchmark established.

Run audit with the server virtual environment's Python and the absolute path to `audit.py`. It writes only local audit artifacts and makes no source API requests.
