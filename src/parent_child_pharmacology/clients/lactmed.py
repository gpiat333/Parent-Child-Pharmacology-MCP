"""lactmed public-source adapter; no MCP registration."""

import html.parser
import json
import re
import sqlite3
import zlib
from pathlib import Path

from parent_child_pharmacology.core.http import http

from .ncbi import _ncbi

LACTMED_HEADINGS = [
    "Summary of Use during Lactation",
    "Drug Levels",
    "Effects in Breastfed Infants",
    "Effects on Lactation and Breastmilk",
    "Alternate Drugs to Consider",
    "References",
]
EXPECTED_CLINICAL_SECTIONS = LACTMED_HEADINGS[:4]

CONCENTRATION = re.compile(
    r"(?<![\w./])(?:[<>\u2264\u2265]\s*)?\d+(?:\.\d+)?"
    r"(?:\s*(?:[-\u2013\u2014]|to)\s*\d+(?:\.\d+)?)?\s*"
    r"(?:ng|mcg|[\u00b5\u03bc]g|ug|mg|nmol|pmol|mmol|micromol|nanograms?|micrograms?|milligrams?)"
    r"\s*(?:/|per\s+)\s*(?:mL|L|milliliters?|liters?)\b",
    re.I,
)


def exposure_measurements(drug_levels):
    """Surface exact concentration expressions, without conversion or specimen inference."""
    sentences = re.split(r"(?<=[.!?])(?:\[[\d,\s-]+\])*\s+(?=[A-Z])", drug_levels)
    passages = []
    for index, sentence in enumerate(sentences):
        values = [m.group(0) for m in CONCENTRATION.finditer(sentence)]
        if values:
            passages.append(
                {
                    "concentration_values_as_reported": values,
                    "source_passage": sentence,
                    "preceding_context": sentences[index - 1] if index else None,
                    "source_section": "Drug Levels",
                }
            )
    infant = re.search(r"\bInfant Levels[.:]\s*(.*)", drug_levels, re.S)
    excerpt = infant.group(1).strip() if infant else None
    return {
        "status": "quantitative_concentrations_extracted"
        if passages
        else "no_quantitative_concentrations_extracted",
        "concentration_passages": passages[:12],
        "additional_passages_omitted": len(passages) > 12,
        "infant_level_excerpt": excerpt,
        "infant_level_section_present_in_returned_text": infant is not None,
        "exhaustive": False,
        "extraction_scope": "Exact concentration expressions from the returned Drug Levels excerpt only. No unit conversion, dose calculation or automatic specimen classification. Read the source passage and preceding context to distinguish milk, maternal serum and infant serum. Empty extraction is not proof that no measurements exist.",
        "presentation_requirement": "Include a Measured exposure row in a summary of this record. Report the retrieved milk concentration values and units with their study context, separately from infant outcomes and administered regimens. Do not replace retrieved numeric concentrations with only low or trace. State infant-level availability or the missing excerpt. If measurements are omitted, explicitly disclose that omission. These are research measurements, not dosing instructions; never convert them to a personal dose.",
    }


def lactmed_payload(sections, max_chars=6000):
    from parent_child_pharmacology.core.source_context import CONTINUITY_NOTICE, evidence_base

    clinical = {h: sections[h] for h in EXPECTED_CLINICAL_SECTIONS if sections.get(h)}
    # Reserve room for every available section before redistributing unused space.
    # A long Drug Levels section must not silently crowd out infant outcomes or
    # effects on lactation. The legacy text field still respects max_chars.
    overhead = sum(len(h) + 2 for h in clinical) + max(0, len(clinical) - 1) * 2
    remaining = max(0, max_chars - overhead)
    budgets = {h: 0 for h in clinical}
    pending = list(clinical)
    while pending and remaining:
        share = max(1, remaining // len(pending))
        for h in pending:
            amount = min(share, remaining, len(clinical[h]) - budgets[h])
            budgets[h] += amount
            remaining -= amount
        pending = [h for h in pending if budgets[h] < len(clinical[h])]
    text = ""
    status = {}
    returned = {}
    for heading, content in clinical.items():
        prefix = ("\n\n" if text else "") + heading + ": "
        piece = content[: budgets[heading]]
        if piece:
            text += prefix + piece
            returned[heading] = piece
        status[heading] = {
            "found": True,
            "characters_in_source_extract": len(content),
            "characters_returned": len(piece),
            "returned": bool(piece),
            "truncated": len(piece) < len(content),
        }
    missing = [h for h in EXPECTED_CLINICAL_SECTIONS if h not in clinical]
    out = {
        "text": text,
        "sections": returned,
        "exposure_measurements": exposure_measurements(returned.get("Drug Levels", "")),
        "sections_found": list(clinical),
        "sections_expected": EXPECTED_CLINICAL_SECTIONS,
        "section_allocation": "Available sections share the text limit; unused space is redistributed. Each section retains its truncation status.",
        "interpretation_contract": {
            "measurements": "Preserve relevant measured milk or infant-serum concentrations and their units separately from outcomes. These are research measurements, not administered doses or dosing instructions. If numeric doses were excluded, omit administered regimens and dose estimates rather than omitting concentration findings.",
            "observations": "Report what was observed and in which population. A symptom monitored in a study is not automatically a clinical recommendation to monitor it.",
            "recommendations": "Attribute monitoring advice to the source only when the returned source explicitly recommends it. If no recommendation is retrieved, state that limitation instead of turning observations into advice.",
            "maternal_effects": "Effects on Lactation and Breastmilk concerns the lactating person. Milk/infant concentrations belong under exposure, not maternal clinical effects.",
        },
        "sections_missing": missing,
        "sections_returned": [h for h, v in status.items() if v["returned"]],
        "sections_omitted_by_limit": [h for h, v in status.items() if not v["returned"]],
        "section_status": status,
        "truncated": any(v["truncated"] for v in status.values()),
        "section_completeness_notice": "Missing sections can reflect source coverage or parser failure; truncated sections are incomplete. Do not present this extract as a complete record.",
        "evidence_base": evidence_base(" ".join(clinical.values())),
        "source_balance_context": {
            "text": clinical.get("Summary of Use during Lactation", "")[:4000] or None,
            "truncated": len(clinical.get("Summary of Use during Lactation", "")) > 4000,
            "source_section": "Summary of Use during Lactation",
            "notice": "Preserve relevant source context when describing adverse findings; this is source text, not a personal treatment plan.",
        },
        "alternatives_policy": {
            "handling": "excluded",
            "present_in_parsed_source": bool(sections.get("Alternate Drugs to Consider")),
            "notice": "Alternate Drugs to Consider is excluded from returned text and synthesis. Consult the linked LactMed source; this tool does not recommend substitutions.",
        },
        "population_context": {"source_population": "lactation", "pregnancy_evidence": False},
        "continuity_of_care_notice": CONTINUITY_NOTICE,
    }
    if not clinical:
        out.update(error="clinical_sections_unavailable", clinical_sections_unavailable=True)
    return out


async def lactmed_search(drug: str, n: int = 5) -> list[dict]:
    drug = drug.replace('"', "").strip()
    ids: list[str] = []
    for term in (f'"{drug}"[Title] AND lactmed[Book]', f"{drug} AND lactmed[Book]"):
        r = await _ncbi("esearch", db="books", term=term, retmax=n, retmode="json")
        ids = r.json()["esearchresult"]["idlist"]
        if ids:
            break
    if not ids:
        return []
    s = (await _ncbi("esummary", db="books", id=",".join(ids), retmode="json")).json()["result"]
    return [
        {
            "id": i,
            "title": s[i].get("title"),
            "url": f"https://www.ncbi.nlm.nih.gov/books/{s[i].get('accessionid', '')}/",
        }
        for i in ids
        if i in s
    ]


class _PageText(html.parser.HTMLParser):
    SKIP = {"script", "style", "nav", "header", "footer"}

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        elif tag in ("p", "div", "h1", "h2", "h3", "h4", "li", "br", "tr"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
        elif tag in ("p", "div", "h1", "h2", "h3", "h4", "li", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def parse_lactmed_html(page: str) -> dict[str, str]:
    p = _PageText()
    p.feed(page)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in "".join(p.parts).split("\n")]
    lookup = {h.lower(): h for h in LACTMED_HEADINGS}
    sections: dict[str, list[str]] = {}
    current = None
    for ln in filter(None, lines):
        key = ln.lower().rstrip(":")
        if current and (
            key == "references"
            or key.startswith(
                (
                    "references ",
                    "substance identification",
                    "administrative information",
                    "copyright notice",
                    "disclaimer:",
                    "bookshelf id:",
                    "related information",
                )
            )
        ):
            break
        if key in lookup:
            current = lookup[key]
            sections.setdefault(current, [])
        elif current:
            sections[current].append(ln)
    return {h: " ".join(t) for h, t in sections.items() if t and h != "References"}


SNAPSHOT = Path(__file__).resolve().parents[1] / "mc" / "data" / "lactmed.sqlite"
_MARKER = re.compile(r"\[(\d+(?:\s*[-\u2013,]\s*\d+)*)\]")


def snapshot_record(stem):
    """Read one record from the bundled official LactMed package (read-only)."""
    if not stem or not SNAPSHOT.exists():
        return None
    con = sqlite3.connect(SNAPSHOT.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        row = con.execute("SELECT payload FROM records WHERE stem = ?", (stem,)).fetchone()
    finally:
        con.close()
    return json.loads(zlib.decompress(row[0])) if row else None


def cited_numbers(text):
    """Expand LactMed citation markers such as [47-53] or [12,15] into reference numbers."""
    numbers = set()
    for group in _MARKER.findall(text or ""):
        for part in re.split(r"\s*,\s*", group):
            bounds = re.split(r"\s*[-\u2013]\s*", part)
            if len(bounds) == 2 and bounds[0].isdigit() and bounds[1].isdigit():
                low, high = int(bounds[0]), int(bounds[1])
                numbers.update(str(n) for n in range(low, min(high, low + 200) + 1))
            elif part.isdigit():
                numbers.add(part)
    return numbers


def reference_links(text, references):
    cited = cited_numbers(text)
    out = []
    for ref in references:
        if ref.get("number") in cited:
            url = (
                f"https://pubmed.ncbi.nlm.nih.gov/{ref['pmid']}/"
                if ref.get("pmid")
                else f"https://doi.org/{ref['doi']}"
                if ref.get("doi")
                else None
            )
            out.append({**ref, "url": url})
    return out


def is_browser_challenge(page):
    head = (page or "")[:4000].lower()
    return "recaptcha" in head or "checking your browser" in head


async def lactmed_record(book_id: str, max_chars: int = 16000) -> dict:
    if not re.fullmatch(r"[0-9]+", book_id):
        return {
            "book_id": book_id,
            "text": "",
            "error": "Invalid book_id. Pass the medicine name in drug, or a numeric id from an earlier result.",
            "url": "https://www.ncbi.nlm.nih.gov/books/NBK501922/",
        }
    s = (
        (await _ncbi("esummary", db="books", id=book_id, retmode="json"))
        .json()["result"]
        .get(book_id, {})
    )
    acc = s.get("accessionid")
    if not acc:
        return {"book_id": book_id, "text": "", "note": "No accession found for this ID"}
    url = f"https://www.ncbi.nlm.nih.gov/books/{acc}/"
    # Search summaries name the record file, e.g. lactmed/chapter/LM328/PMC.
    parts = (s.get("id") or "").split("/")
    stem = parts[2] if len(parts) > 2 and parts[0] == "lactmed" else None
    record = snapshot_record(stem)
    if record:
        from parent_child_pharmacology.core.freshness import lactmed_freshness

        payload = lactmed_payload(record["sections"], max_chars)
        links = reference_links(payload["text"], record["references"])
        return {
            "source": "snapshot:lactmed",
            "book_id": book_id,
            "title": s.get("title") or record["title"],
            "url": url,
            "record_revised_on": record.get("revised_on"),
            "data_freshness": lactmed_freshness(record.get("revised_on")),
            **payload,
            "references": links,
            "references_total_in_record": len(record["references"]),
            "citation_instructions": "Numbers in square brackets, such as [54], are LactMed's own citations. "
            "Link each finding you report to its study using the references list (PubMed URL when available). "
            "Only references cited in the returned text are listed.",
        }
    r = await http.request("GET", url, ttl=86400, interval=0.4)
    if is_browser_challenge(r.text):
        return {
            "book_id": book_id,
            "title": s.get("title"),
            "url": url,
            "text": "",
            "error": "source_blocked_by_browser_check",
            "note": "NCBI returned a browser check instead of the record, and this server does not bypass it. "
            "The record is not in the bundled LactMed snapshot. Open the link to read it.",
        }
    sections = parse_lactmed_html(r.text)
    return {
        "source": "live:ncbi",
        "book_id": book_id,
        "title": s.get("title"),
        "url": url,
        **lactmed_payload(sections, max_chars),
    }


# Common vaccine names mapped to LactMed record titles (LactMed groups vaccines by type).
VACCINE_TITLES = {
    "flu": "Influenza Vaccines",
    "influenza": "Influenza Vaccines",
    "mmr": "Measles-Mumps-Rubella Vaccine",
    "measles": "Measles-Mumps-Rubella Vaccine",
    "mmrv": "Measles-Mumps-Rubella-Varicella Vaccine",
    "tdap": "Diphtheria-Tetanus-Pertussis Vaccines",
    "dtap": "Diphtheria-Tetanus-Pertussis Vaccines",
    "whooping cough": "Diphtheria-Tetanus-Pertussis Vaccines",
    "pertussis": "Diphtheria-Tetanus-Pertussis Vaccines",
    "rsv": "Respiratory Syncytial Virus Vaccine",
    "respiratory syncytial virus": "Respiratory Syncytial Virus Vaccine",
    "hpv": "Human Papillomavirus Vaccines",
    "covid": "COVID-19 Vaccines",
    "covid-19": "COVID-19 Vaccines",
    "chickenpox": "Varicella Vaccine",
    "varicella": "Varicella Vaccine",
    "shingles": "Zoster Vaccines",
    "hep b": "Hepatitis B Vaccine",
    "hepatitis b": "Hepatitis B Vaccine",
    "hep a": "Hepatitis A Vaccine",
    "hepatitis a": "Hepatitis A Vaccine",
    "hib": "Haemophilus Vaccines",
    "polio": "Poliovirus Vaccines",
    "pneumococcal": "Pneumococcal Vaccines",
    "meningococcal": "Meningococcal Vaccines",
    "rotavirus": "Rotavirus Vaccines",
}


def snapshot_title_match(name):
    """Exact LactMed record title for a common name, from the bundled package's titles."""
    q = re.sub(r"\s+", " ", (name or "").lower()).strip()
    base = re.sub(
        r"\s*\b(?:vaccines?|vaccinations?|shots?|jabs?|immuni[sz]ations?)\b\s*", " ", q
    ).strip()
    if re.search(r"\b(?:vaccin\w*|shots?|jabs?|immuni[sz]\w*)\b", q) or q in VACCINE_TITLES:
        if base in VACCINE_TITLES:
            return VACCINE_TITLES[base]
    if not SNAPSHOT.exists():
        return None
    con = sqlite3.connect(SNAPSHOT.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        titles = [r[0] for r in con.execute("SELECT title FROM records")]
    finally:
        con.close()
    lowered = {t.lower(): t for t in titles}
    for candidate in (q, q + "s", q[:-1] if q.endswith("s") else None):
        if candidate and candidate in lowered:
            return lowered[candidate]
    return None
