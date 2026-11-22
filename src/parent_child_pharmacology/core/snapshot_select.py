"""Deterministic filtering of captured MPRINT metadata; a client utility only."""

SCHEMA = {
    "type": "function",
    "function": {
        "name": "select_snapshot_records",
        "description": "Filter and count distinct PMIDs from captured find_mprint_records pages using joined Silver labels and exported table counts. No new retrieval, clinical interpretation or invented fields. For all-record questions require complete pagination; for an explicitly bounded candidate cohort use require_complete=false. Returns the filtered distinct_count and selected records for return_source_value.",
        "parameters": {
            "type": "object",
            "properties": {
                "source_call_indices": {
                    "type": "array",
                    "items": {"type": "integer", "minimum": 0},
                    "minItems": 1,
                    "maxItems": 128,
                },
                "required_labels": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
                "excluded_labels": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
                "zero_outcome_table": {"enum": [None, "PK_summary", "PE_CT"]},
                "require_complete": {"type": "boolean"},
                "sort_pmid": {"enum": ["ascending", "descending"]},
                "limit": {"type": ["integer", "null"], "minimum": 1, "maximum": 20},
            },
            "required": [
                "source_call_indices",
                "required_labels",
                "excluded_labels",
                "zero_outcome_table",
                "require_complete",
                "sort_pmid",
                "limit",
            ],
            "additionalProperties": False,
        },
    },
}


def select_records(
    calls,
    source_call_indices,
    required_labels,
    excluded_labels,
    zero_outcome_table,
    require_complete,
    sort_pmid,
    limit,
):
    if (
        not isinstance(source_call_indices, list)
        or not 1 <= len(source_call_indices) <= 128
        or len(set(source_call_indices)) != len(source_call_indices)
    ):
        raise ValueError("Choose distinct captured pages")
    if (
        type(require_complete) is not bool
        or sort_pmid not in ["ascending", "descending"]
        or limit is not None
        and (type(limit) is not int or not 1 <= limit <= 20)
    ):
        raise ValueError("Invalid selection settings")
    if zero_outcome_table not in [None, "PK_summary", "PE_CT"]:
        raise ValueError("Unknown outcome table")
    if not all(
        isinstance(v, list) and len(v) <= 20 and all(isinstance(x, str) for x in v)
        for v in [required_labels, excluded_labels]
    ):
        raise ValueError("Labels must be lists of source codes")
    required, excluded = set(required_labels), set(excluded_labels)
    if required & excluded:
        raise ValueError("A label cannot be required and excluded")
    pages = []
    signature = None
    for i in source_call_indices:
        if type(i) is not int or not 0 <= i < len(calls):
            raise ValueError("Unknown source call")
        call = calls[i]
        r = call.get("result", {})
        args = call.get("arguments", {})
        if (
            call.get("tool") != "find_mprint_records"
            or not isinstance(r, dict)
            or r.get("error")
            or not isinstance(r.get("results"), list)
        ):
            raise ValueError("Use successful metadata pages")
        sig = (
            args.get("drug"),
            args.get("population"),
            args.get("study_type"),
            args.get("pmid"),
            r.get("dataset_revision"),
        )
        if signature is None:
            signature = sig
        if signature != sig:
            raise ValueError("Do not combine different queries or revisions")
        if not (required | excluded) <= set(r.get("classification_legend", {})):
            raise ValueError("Use label codes from the source legend")
        pages.append((i, r))
    # A follow-up identifier lookup cannot redefine the candidate universe.
    anchor = next(
        (
            i
            for i, c in enumerate(calls)
            if c.get("tool") == "find_mprint_records"
            and c.get("arguments", {}).get("drug")
            and not c.get("arguments", {}).get("pmid")
            and isinstance(c.get("result"), dict)
            and not c["result"].get("error")
            and isinstance(c["result"].get("results"), list)
            and c["result"]["results"]
        ),
        None,
    )
    if anchor is not None and anchor not in source_call_indices:
        raise ValueError(
            "Selection must include the original candidate page; a narrowed PMID lookup or replacement query cannot change the cohort."
        )
    if require_complete:
        offset = 0
        for _, r in sorted(pages, key=lambda page: page[1].get("offset", -1)):
            if r.get("offset") != offset:
                raise ValueError("Missing or overlapping pages")
            offset += len(r["results"])
            if r.get("has_more") is True and r.get("next_offset") != offset:
                raise ValueError("Invalid continuation")
        last = max(pages, key=lambda page: page[1].get("offset", -1))[1]
        if last.get("has_more") is not False or offset != last.get("matching_records"):
            raise ValueError("Complete the source pagination before counting")
    found = {}
    for i, r in pages:
        for row in r["results"]:
            pmid = row.get("pmid")
            if not isinstance(pmid, str) or not pmid.isdecimal() or not pmid.isascii():
                raise ValueError("Unknown record identity")
            classifications = row.get("silver_classifications")
            if not isinstance(classifications, list) or any(
                not isinstance(c, dict) or not isinstance(c.get("study_type"), str)
                for c in classifications
            ):
                raise ValueError("Fetch joined classification metadata")
            labels = {c["study_type"] for c in classifications}
            if not required <= labels or excluded & labels:
                continue
            if zero_outcome_table is not None:
                count = row.get("exported_outcome_rows", {}).get(zero_outcome_table)
                if type(count) is not int or count < 0:
                    raise ValueError("Exported table count is unknown")
                if count != 0:
                    continue
            if pmid not in found:
                found[pmid] = {**row, "source_call_index": i}
    ordered = sorted(
        found.values(), key=lambda r: int(r["pmid"]), reverse=sort_pmid == "descending"
    )
    return {
        "distinct_count": len(ordered),
        "results": ordered if limit is None else ordered[:limit],
        "source_call_indices": source_call_indices,
        "required_labels": sorted(required),
        "excluded_labels": sorted(excluded),
        "zero_outcome_table": zero_outcome_table,
        "complete_source_pages_required": require_complete,
        "scope": "Distinct captured PMIDs after explicit metadata filters; exported zero rows is not absence of outcomes in the paper. A limited result list does not change distinct_count.",
    }
