"""dailymed public-source adapter; no MCP registration."""

import re
import xml.etree.ElementTree as ET

from parent_child_pharmacology.core.http import http

from .parsing import text_of
from .pllr import parse_pllr

DAILYMED = "https://dailymed.nlm.nih.gov/dailymed/services/v2"
LOINC_SECTIONS = {"42228-7": "pregnancy", "77290-5": "lactation", "34081-0": "pediatric_use"}
SECTION_TITLES = {
    "pregnancy": "pregnancy",
    "lactation": "lactation",
    "nursing mothers": "lactation",
    "pediatric use": "pediatric_use",
    "geriatric use": "geriatric_use",
}

MEDICINE_TAKER_SECTIONS = [
    "adverse_reactions",
    "warnings",
    "warnings_and_precautions",
    "boxed_warning",
    "drug_interactions",
]


def parse_medicine_taker_sections(xml):
    """The same label's medicine-taker sections, separate from population sections."""
    ns = {"h": "urn:hl7-org:v3"}
    codes = {
        "34084-4": "adverse_reactions",
        "34071-1": "warnings",
        "43685-7": "warnings_and_precautions",
        "34066-1": "boxed_warning",
        "34073-7": "drug_interactions",
    }
    titles = {key.replace("_", " "): key for key in MEDICINE_TAKER_SECTIONS}
    out = {}
    for sec in ET.fromstring(xml).iterfind(".//h:section", ns):
        title = re.sub(r"^[\d.\s]+", "", text_of(sec.find("h:title", ns))).strip().lower()
        code = sec.find("h:code", ns)
        key = titles.get(title) or (
            codes.get(code.get("code")) if not title and code is not None else None
        )
        text = text_of(sec.find("h:text", ns))
        if key and text:
            out.setdefault(
                key,
                {
                    "text": text[:4000],
                    "truncated": len(text) > 4000,
                    "interpretation": "Product-label text; not a diagnosis or recommendation for this individual.",
                },
            )
    return out


PRODUCT_DESCRIPTION_CODES = {
    "34089-3": "description",
    "55106-9": "active_ingredients",
    "51727-6": "inactive_ingredients",
}
PRODUCT_DESCRIPTION_TITLES = {
    "description": "description",
    "active ingredient": "active_ingredients",
    "active ingredients": "active_ingredients",
    "inactive ingredient": "inactive_ingredients",
    "inactive ingredients": "inactive_ingredients",
}


def parse_product_description(xml, max_chars=3000):
    """What the product contains, from the same label: section 11 (chemical name, molecular
    formula and weight, inactive ingredients) or OTC active and inactive ingredient lists.
    Structural formula images are not text and are not returned."""
    ns = {"h": "urn:hl7-org:v3"}
    out = {}
    for sec in ET.fromstring(xml).iterfind(".//h:section", ns):
        title = re.sub(r"^[\d.\s]+", "", text_of(sec.find("h:title", ns))).strip().lower()
        code = sec.find("h:code", ns)
        key = PRODUCT_DESCRIPTION_TITLES.get(title) or (
            PRODUCT_DESCRIPTION_CODES.get(code.get("code")) if code is not None else None
        )
        text = text_of(sec.find("h:text", ns))
        if key and text and key not in out:
            out[key] = {"text": text[:max_chars], "truncated": len(text) > max_chars}
    return out


APPROVED_USE_CODES = {"34067-9": "indications_and_usage", "34092-7": "clinical_studies"}
APPROVED_USE_TITLES = {
    "indications and usage": "indications_and_usage",
    "indications & usage": "indications_and_usage",
    "clinical studies": "clinical_studies",
}


def parse_approved_use_sections(xml, max_chars=3000):
    """What the product is approved for and the studies behind it (mostly adults)."""
    ns = {"h": "urn:hl7-org:v3"}
    out = {}
    for sec in ET.fromstring(xml).iterfind(".//h:section", ns):
        title = re.sub(r"^[\d.\s]+", "", text_of(sec.find("h:title", ns))).strip().lower()
        code = sec.find("h:code", ns)
        key = APPROVED_USE_TITLES.get(title) or (
            APPROVED_USE_CODES.get(code.get("code")) if code is not None else None
        )
        text = text_of(sec.find("h:text", ns))
        if key and text and key not in out:
            out[key] = {"text": text[:max_chars], "truncated": len(text) > max_chars}
    return out


def parse_dailymed_sections(xml: str, max_chars: int = 4000) -> dict[str, str]:
    ns = {"h": "urn:hl7-org:v3"}
    found = {}
    for sec in ET.fromstring(xml).iterfind(".//h:section", ns):
        c = sec.find("h:code", ns)
        title = re.sub(r"^[\d.\s]+", "", text_of(sec.find("h:title", ns))).strip().lower()
        key = SECTION_TITLES.get(title)
        # Some source SPLs miscode adjacent sections. Never call explicit
        # geriatric text pediatric merely because its code says pediatric.
        if key is None and not title and c is not None:
            key = LOINC_SECTIONS.get(c.get("code"))
        # OTC labels use one combined section (LOINC 53414-9). Preserve
        # its scope rather than duplicating it into two independent sections.
        if (
            key is None
            and c is not None
            and c.get("code") == "53414-9"
            and title
            in {
                "",
                "if pregnant or breast-feeding",
                "if pregnant or breast-feeding:",
                "pregnancy or breast feeding",
                "pregnancy or breast-feeding",
            }
        ):
            key = "pregnancy_lactation"
        if key in {"pregnancy", "lactation", "pediatric_use", "pregnancy_lactation"}:
            content = text_of(sec.find("h:text", ns))
            if content:
                found.setdefault(key, content[:max_chars])
    return found


def dailymed_section_warnings(xml: str) -> list[dict]:
    ns = {"h": "urn:hl7-org:v3"}
    warnings = []
    for sec in ET.fromstring(xml).iterfind(".//h:section", ns):
        title = text_of(sec.find("h:title", ns))
        normalized = re.sub(r"^[\d.\s]+", "", title).strip().lower()
        code = sec.find("h:code", ns)
        if normalized in SECTION_TITLES and code is not None:
            key = SECTION_TITLES[normalized]
            expected = {
                "pregnancy": "42228-7",
                "lactation": "77290-5",
                "pediatric_use": "34081-0",
                "geriatric_use": "34082-8",
            }[key]
            if normalized == "nursing mothers":
                expected = "34080-2"  # Valid older SPL heading/code, not a mismatch.
            if code.get("code") != expected:
                warnings.append(
                    {
                        "title": title,
                        "code": code.get("code"),
                        "note": "Source title/code mismatch; classified by explicit title. Verify the linked label.",
                    }
                )
    return warnings


def label_provenance(
    xml, item, *, position=1, fetched=1, total=None, rule="First API-ordered name match."
):
    root = ET.fromstring(xml)
    ns = {"h": "urn:hl7-org:v3"}
    version = root.find("h:versionNumber", ns)
    effective = root.find("h:effectiveTime", ns)
    date = effective.get("value") if effective is not None else None
    if date and re.fullmatch(r"\d{8}", date):
        date = date[:4] + "-" + date[4:6] + "-" + date[6:]
    return {
        "spl_version": version.get("value") if version is not None else item.get("spl_version"),
        "effective_date": date,
        "published_date": item.get("published_date"),
        "labeler": text_of(
            root.find(".//h:author/h:assignedEntity/h:representedOrganization/h:name", ns)
        )
        or None,
        "selection_basis": {
            "rule": rule,
            "candidate_position": position,
            "candidates_examined": position,
            "candidates_fetched": fetched,
            "total_matching_spls": total,
            "most_recent_effective_date_claimed": False,
            "exact_rxcui_match_claimed": False,
        },
        "label_currency_notice": "DailyMed publishes in-use labeling, which can differ from the latest FDA-approved labeling. Effective date is a source document date, not a guarantee of current approval status.",
    }


async def dailymed_label(drug: str) -> dict:
    r = await http.request(
        "GET", f"{DAILYMED}/spls.json", params={"drug_name": drug, "pagesize": 5}, ttl=86400
    )
    data = r.json()
    candidates = data.get("data", [])
    for index, item in enumerate(candidates):
        x = await http.request("GET", f"{DAILYMED}/spls/{item['setid']}.xml", ttl=86400)
        secs = parse_dailymed_sections(x.text)
        if secs:
            adult = parse_medicine_taker_sections(x.text)
            root = ET.fromstring(x.text)
            ns = {"h": "urn:hl7-org:v3"}
            version = root.find("h:versionNumber", ns)
            effective = root.find("h:effectiveTime", ns)
            full_sections = parse_dailymed_sections(x.text, max_chars=len(x.text) + 1)
            truncations = {
                key: len(full_sections.get(key, "")) > len(value) for key, value in secs.items()
            }
            date = effective.get("value") if effective is not None else None
            if date and re.fullmatch(r"\d{8}", date):
                date = date[:4] + "-" + date[4:6] + "-" + date[6:]
            return {
                "setid": item["setid"],
                "title": item["title"],
                "product_identification": {
                    "product": item["title"],
                    "instruction": "Name this exact product when reporting anything from this label. "
                    "It is one matching product, not every brand or formulation of the medicine.",
                },
                "sections": secs,
                "medicine_taker_sections": adult,
                "medicine_taker_sections_expected": MEDICINE_TAKER_SECTIONS,
                "medicine_taker_sections_missing": [
                    k for k in MEDICINE_TAKER_SECTIONS if k not in adult
                ],
                "medicine_taker_sections_truncated": any(v["truncated"] for v in adult.values()),
                "product_description": parse_product_description(x.text),
                "approved_use_sections": parse_approved_use_sections(x.text),
                "approved_use_notice": "Approved uses (indications) and the clinical studies behind them, mostly in adults. A use not listed is off-label; off-label use in children is common and is not recorded in the label. Approval in adults does not establish a dose, safety or effectiveness in children.",
                "product_description_notice": "What this product contains, from the same label: chemical name, molecular formula and weight, and active and inactive ingredients where the label lists them. Structural formula images are not returned. Describes this one product, not other brands or formulations.",
                "section_scope_notice": "sections contains pregnancy, lactation and pediatric-use text. medicine_taker_sections contains adverse reactions and warnings from the SAME selected label. For adult-versus-infant comparisons, inspect both groups and LactMed; do not treat a population section as the full adult warning profile. Missing sections are extraction limitations, not proof of absence.",
                "spl_version": version.get("value")
                if version is not None
                else item.get("spl_version"),
                "effective_date": date,
                "published_date": item.get("published_date"),
                "labeler": text_of(
                    root.find(".//h:author/h:assignedEntity/h:representedOrganization/h:name", ns)
                )
                or None,
                "selection_basis": {
                    "rule": "First label with extractable requested sections among the first five API-ordered name matches.",
                    "candidate_position": index + 1,
                    "candidates_examined": index + 1,
                    "candidates_fetched": len(candidates),
                    "total_matching_spls": data.get("metadata", {}).get("total_elements"),
                    "most_recent_effective_date_claimed": False,
                    "exact_rxcui_match_claimed": False,
                },
                "sections_found": list(secs),
                "sections_missing": [
                    k for k in ("pregnancy", "lactation", "pediatric_use") if k not in secs
                ],
                "sections_truncated": truncations,
                "truncated": any(truncations.values()),
                "label_currency_notice": "DailyMed publishes in-use labeling, which can differ from the latest FDA-approved labeling. Effective date is a source document date, not a guarantee of current approval status.",
                "missing_standalone_sections": [
                    k for k in ("pregnancy", "lactation", "pediatric_use") if k not in secs
                ],
                "selection_note": "One matching product label, not all formulations. A combined OTC pregnancy_lactation warning is not a standalone pediatric-use section. Missing sections do not establish safety or absence of information elsewhere in the label.",
                "warnings": dailymed_section_warnings(x.text),
                "pllr_8_1": parse_pllr(xml=x.text),
                "url": f"https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid={item['setid']}",
            }
    return {}
