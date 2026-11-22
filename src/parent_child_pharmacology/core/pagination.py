"""Uniform continuation disclosure without inventing upstream cursors."""


def add_pagination(result, name, arguments):
    if "pagination" in result:
        return result
    rows = result.get("results", [])
    metadata = result.get("search_metadata", {})
    if name == "search_literature" and result.get("source") == "live:pubmed":
        offset = arguments.get("offset", 0)
        limit = arguments.get("max_results", 10)
        count = metadata.get("count")
        total = int(count) if str(count).isdigit() else None
        end = offset + limit
        more = end < total if total is not None else None
        next_offset = end if more and end < 10000 else None
        result["pagination"] = {
            "offset": offset,
            "limit": limit,
            "returned": len(rows),
            "total": total,
            "has_more": more,
            "next_offset": next_offset,
            "continuation_supported": next_offset is not None,
            "notice": "Live relevance ordering can change between calls. PubMed retrieval is capped at 10,000 hits; narrow the query beyond that limit.",
        }
    else:
        supported = result.get("next_offset") is not None
        result["pagination"] = {
            "returned": len(rows),
            "has_more": result.get("has_more"),
            "next_offset": result.get("next_offset"),
            "continuation_supported": supported,
            "notice": "Use only a returned continuation. Otherwise this is a bounded response with unknown completeness, not an exhaustive result set. Source-specific page arguments remain documented in tool schemas.",
        }
    return result
