# MPRINT snapshot benchmark v1

Ten independent, read-only exact-answer questions for MCP tool use. Each question includes the fixed dataset revision and an explicit output format. This is a data retrieval/analysis benchmark, not a clinical recommendation benchmark.

## Files

- `evaluation.xml`: authoritative question/answer pairs, in the GSA mcp-builder evaluation format.
- `dataset.csv`: the same 10 rows, with `id,query,responses` columns.
- `verification.json`: inspected tool schemas, snapshot resources, actual requests and returned MCP evidence, trace IDs, programmatically checked answer derivations, and question-level references.

## Provenance and verification

MPRINT revision `4bdee90dff3610816e86d0eed29b4c4d0fe76e89`, metadata retrieved 2026-11-17T20:46:16.556578+00:00; outcomes retrieved 2026-11-17T21:33:46.760396+00:00. Verified 2026-11-22 UTC through the MCP server. Initial discovery used stdio with USE_LAKEHOUSE=false; later verification used the local stateless HTTP MCP at 127.0.0.1:8772 after a Windows stdio-client shutdown hang. Both transports reported the same dataset revision. The transient local HTTP port is not a benchmark dependency.

The independent exploration agent read mcp-builder/SKILL.md and references/evaluation.md, inspected schemas before tool calls, and did not read application implementation or tests. Only read-only find_mprint_records/get_mprint_details and resources were used. All bounded result requests used max_results below 10; outcome continuations were followed using returned next_offset values. No model evaluation was executed while authoring these files.

## Coverage and limitations

Questions exercise drug/population/study-type discovery; joins between Gold metadata, Gold outcome tables and Silver automated classifications; source population versus broad search bands; actual row exposure versus study context; pagination; workbook duplication; per-group denominators; exact answer formatting; and arithmetic over explicit source values. Do not substitute live PubMed/RxNorm results for the fixed snapshot.

Gold search has no pagination, so unrestricted exhaustive questions would be misleading. Small cohorts are complete only when matching_records equals the number returned. Two tasks explicitly define the first nine descending-numeric-PMID candidates; numeric PMID order is not publication-date order. Outcome tables support pagination.

This set is not uniformly dozens-of-calls difficulty: questions 3, 6 and 10 are moderate. The most demanding tasks join nine classifications and page 24 or 104 rows while rejecting duplicate workbook copies. Questions are logically independent, although some reuse cohorts. Single-answer formats include numbers, DOI strings, an exposure name and a site label.

Automated Silver labels are not curated Gold clinical findings. Null fields and absent exported rows do not establish zero clinical events, lack of original-paper evidence, safety, causality, study quality, or MPRINT funding. Source rows can be internally inconsistent; benchmark arithmetic deliberately follows specified exported fields and makes no clinical inference. Never pool duplicate workbook copies as independent studies.

The benchmark runner should evaluate the model response against the CSV responses value while retaining the complete agent transcript separately for safety/citation review. A successful exact answer alone is not evidence of clinical suitability.
