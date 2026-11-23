"""rxnorm public-source adapter; no MCP registration."""

import re

from parent_child_pharmacology.core.http import http

RXNAV = "https://rxnav.nlm.nih.gov/REST"
VACCINE_NOTE = (
    "RxNorm lists vaccines by specific product, not by common names such as 'flu vaccine' or 'Tdap'. "
    "Ask for the product or brand name on the vaccine record. For breastfeeding, search_lactmed finds "
    "LactMed's vaccine records by type (for example, Influenza Vaccines)."
)


async def products_containing_ingredient(ingredient, n=20):
    norm = await rxnorm_normalize(ingredient)
    if not norm.get("found") or norm.get("requires_confirmation") or norm.get("term_type") != "IN":
        return {
            "source": "live:rxnorm",
            "requires_confirmation": True,
            "resolved": norm,
            "results": [],
            "note": "Provide one exact active ingredient, not a combination or approximate medicine identity.",
        }
    uri = f"{RXNAV}/rxcui/{norm['rxcui']}/related.json"
    data = (await http.request("GET", uri, params={"tty": "SCD SBD"}, ttl=86400)).json()
    rows = []
    seen = set()
    for group in data.get("relatedGroup", {}).get("conceptGroup", []):
        if group.get("tty") not in {"SCD", "SBD"}:
            continue
        for p in group.get("conceptProperties", []):
            if p.get("rxcui") in seen:
                continue
            seen.add(p.get("rxcui"))
            rows.append(
                {
                    "rxcui": p.get("rxcui"),
                    "name": p.get("name"),
                    "term_type": group["tty"],
                    "url": f"{RXNAV}/rxcui/{p.get('rxcui')}/properties.json",
                }
            )
    rows.sort(key=lambda p: (p.get("name") or "").casefold())
    return {
        "source": "live:rxnorm",
        "ingredient": norm,
        "url": uri + "?tty=SCD+SBD",
        "results": rows[:n],
        "total_related_products": len(rows),
        "results_truncated": len(rows) > n,
        "display_order": "alphabetical, not recommended or ranked",
        "caveat": "Drug-identity navigation to help recognize an ingredient appearing in multiple products, including pediatric combination products. This is not a duplicate-dose calculation, dosing/safety check, product recommendation, complete market inventory or verification of a package in hand. Check each exact label with a pharmacist.",
    }


async def rxnorm_normalize(name: str) -> dict:
    name = name.strip()
    if not name:
        return {
            "found": False,
            "error": "empty_drug_name",
            "requires_confirmation": True,
            "note": "Provide a nonempty generic or brand name.",
            "url": "https://rxnav.nlm.nih.gov/",
        }
    exact = (
        await http.request(
            "GET", f"{RXNAV}/rxcui.json", params={"name": name, "search": 0}, ttl=86400
        )
    ).json()
    exact_ids = (exact.get("idGroup") or {}).get("rxnormId") or []
    cands = []
    if not exact_ids:
        r = await http.request(
            "GET",
            f"{RXNAV}/approximateTerm.json",
            params={"term": name, "maxEntries": 3},
            ttl=86400,
        )
        cands = (r.json().get("approximateGroup") or {}).get("candidate") or []
    if not exact_ids and not cands:
        out = {"found": False, "input": name, "url": "https://rxnav.nlm.nih.gov/"}
        if re.search(r"\b(?:vaccin\w*|shots?|immuni[sz]\w*|tdap|dtap|mmr|rsv|hpv)\b", name, re.I):
            out["note"] = VACCINE_NOTE
        return out
    rxcui = exact_ids[0] if exact_ids else cands[0]["rxcui"]
    props = (
        await http.request("GET", f"{RXNAV}/rxcui/{rxcui}/properties.json", ttl=86400)
    ).json().get("properties") or {}
    ingredients: list[str] = []
    if not props.get("name") or not props.get("tty"):
        return {
            "found": False,
            "input": name,
            "requires_confirmation": True,
            "note": VACCINE_NOTE
            if re.search(
                r"\b(?:vaccin\w*|shots?|immuni[sz]\w*|tdap|dtap|mmr|rsv|hpv)\b", name, re.I
            )
            else "No verified active RxNorm identity. Check spelling with a pharmacist or original record.",
            "url": "https://rxnav.nlm.nih.gov/",
        }
    if props.get("tty") == "IN":
        ingredients = [props["name"]]
    else:
        rel = (
            await http.request(
                "GET", f"{RXNAV}/rxcui/{rxcui}/related.json", params={"tty": "IN MIN"}, ttl=86400
            )
        ).json()
        for g in rel.get("relatedGroup", {}).get("conceptGroup", []):
            if g.get("tty") == "IN":
                ingredients += [c["name"] for c in g.get("conceptProperties", [])]
    return {
        "found": bool(ingredients),
        "input": name,
        "rxcui": rxcui,
        "matched_name": props.get("name"),
        "term_type": props.get("tty"),
        "ingredients": list(dict.fromkeys(ingredients)),
        "match_type": "exact" if exact_ids else "approximate",
        "requires_confirmation": len(exact_ids) != 1 or not bool(ingredients),
        "url": f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/properties.json",
    }
