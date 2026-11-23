"""Per-group statistics over captured MPRINT outcome rows; a client utility, not an MCP tool.

Comparing groups (each exposure, arm or site) by hand invites skipped groups and copying a
label from the wrong row. This computes the statistic for EVERY group from the captured rows
and returns each group's exact label for return_source_value. It judges arithmetic only.
"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

STATISTICS = ["range", "max", "min", "mean", "sum", "count"]

SCHEMA = {
    "type": "function",
    "function": {
        "name": "aggregate_outcome_rows",
        "description": "Compute one statistic for EVERY group of rows in a captured get_mprint_details result, for example the spread (max minus min) of Value for each Exposure, or the count of rows per Sub-category. Optional exact-match filters keep only rows whose field equals a value. Groups are sorted by the statistic, largest first, and each group's exact source label can be copied with return_source_value from /groups/N/group. No new retrieval or clinical interpretation.",
        "parameters": {
            "type": "object",
            "properties": {
                "source_call_index": {"type": "integer", "minimum": 0},
                "group_field": {"type": "string", "maxLength": 128},
                "value_field": {"type": "string", "maxLength": 128},
                "statistic": {"enum": STATISTICS},
                "filters": {
                    "type": "array",
                    "maxItems": 10,
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string", "maxLength": 128},
                            "equals": {"type": "string", "maxLength": 512},
                        },
                        "required": ["field", "equals"],
                        "additionalProperties": False,
                    },
                },
                "decimal_places": {"type": "integer", "minimum": 0, "maximum": 8},
            },
            "required": [
                "source_call_index",
                "group_field",
                "value_field",
                "statistic",
                "filters",
                "decimal_places",
            ],
            "additionalProperties": False,
        },
    },
}


def _fields(row):
    return row.get("source_fields") if isinstance(row.get("source_fields"), dict) else row


def aggregate_rows(
    calls, source_call_index, group_field, value_field, statistic, filters, decimal_places
):
    if type(source_call_index) is not int or not 0 <= source_call_index < len(calls):
        raise ValueError("Unknown source call")
    call = calls[source_call_index]
    if call.get("tool") != "get_mprint_details":
        raise ValueError("Group statistics use a captured get_mprint_details result")
    if statistic not in STATISTICS:
        raise ValueError("Unsupported statistic")
    if type(decimal_places) is not int or not 0 <= decimal_places <= 8:
        raise ValueError("Use zero to eight decimal places")
    if not isinstance(filters, list) or len(filters) > 10:
        raise ValueError("Use at most ten filters")
    result = call.get("result")
    if not isinstance(result, dict) or result.get("error"):
        raise ValueError("Source result failed")
    rows = result.get("results") or []
    groups, excluded = {}, []
    for index, row in enumerate(rows):
        fields = _fields(row)
        if any(str(fields.get(f["field"], "")).strip() != f["equals"].strip() for f in filters):
            continue
        label = fields.get(group_field)
        if label is None or not str(label).strip():
            excluded.append({"row": index, "reason": f"missing {group_field}"})
            continue
        group = groups.setdefault(str(label), {"group": str(label), "rows": [], "values": []})
        group["rows"].append(index)
        if statistic == "count":
            continue
        try:
            value = Decimal(str(fields.get(value_field)).strip())
            if not value.is_finite():
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            excluded.append({"row": index, "reason": f"non-numeric {value_field}"})
            group["rows"].pop()
            continue
        group["values"].append(value)
    if not groups:
        raise ValueError("No rows matched; check group_field, value_field and filters")
    quantum = Decimal(1).scaleb(-decimal_places)
    out = []
    for group in groups.values():
        values = group["values"]
        if statistic == "count":
            stat = Decimal(len(group["rows"]))
        elif not values:
            continue
        elif statistic == "range":
            stat = max(values) - min(values)
        elif statistic == "max":
            stat = max(values)
        elif statistic == "min":
            stat = min(values)
        elif statistic == "sum":
            stat = sum(values)
        else:
            stat = sum(values) / len(values)
        out.append(
            {
                "group": group["group"],
                "statistic_value": format(stat.quantize(quantum, rounding=ROUND_HALF_UP), "f"),
                "row_indices": group["rows"],
                "values": [format(v, "f") for v in values],
                "_sort": stat,
            }
        )
    out.sort(key=lambda g: g["_sort"], reverse=True)
    top = out[0]["_sort"] if out else None
    tied = sum(g["_sort"] == top for g in out) > 1
    for g in out:
        g["tied_for_largest"] = tied and g["_sort"] == top
    for g in out:
        del g["_sort"]
    return {
        "pmid": result.get("pmid")
        or (str(_fields(rows[0]).get("PMID", "")).split(".")[0] if rows else None),
        "statistic": statistic,
        "group_field": group_field,
        "value_field": value_field,
        "filters": filters,
        "groups": out,
        "groups_compared": len(out),
        "excluded_rows": excluded,
        "scope": "Arithmetic over captured rows only; source selection and clinical meaning remain unverified.",
    }
