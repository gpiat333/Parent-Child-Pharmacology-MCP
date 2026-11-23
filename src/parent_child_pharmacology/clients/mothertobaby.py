"""MotherToBaby fact sheet metadata from NCBI Bookshelf (collection NBK582980); no MCP registration.

Only the official E-utilities search and summary services are used. Fact sheet page text is
not retrieved: Bookshelf pages can present a browser challenge to automated clients, and this
server never attempts to bypass one.
"""

import html
import re

from .ncbi import _ncbi

BOOK = "mtb"
COLLECTION_URL = "https://www.ncbi.nlm.nih.gov/books/NBK582980/"
# Bookshelf bookinfo names each fact sheet document, e.g. id="sertraline-en" role="document".
_DOCUMENT = re.compile(r'id="([^"]+)" role="document"[^>]*><Title>([^<]*)</Title>')


def _language(document_id):
    # Bookshelf document ids end in -en (English) or -sp (Spanish), e.g. sertraline-sp.
    return {"en": "en", "sp": "es"}.get((document_id or "").rsplit("-", 1)[-1], "unknown")


def _stem(document_id):
    return (document_id or "").rsplit("-", 1)[0].replace("-", " ").lower()


async def fact_sheet_search(drug: str, n: int = 5) -> list[dict]:
    """Return fact sheets whose document id or title names the medicine, English and Spanish.

    Spanish sheets keep the English stem in their id (sertraline-sp is "Sertralina"), so an
    English name finds both. Sheets that only mention the medicine in passing are excluded.
    """
    drug = drug.replace('"', "").strip()
    needle = drug.lower()
    r = await _ncbi(
        "esearch", db="books", term=f"{drug} AND {BOOK}[book]", retmax=60, retmode="json"
    )
    ids = r.json()["esearchresult"]["idlist"]
    if not ids:
        return []
    summary = (await _ncbi("esummary", db="books", id=",".join(ids), retmode="json")).json()[
        "result"
    ]
    sheets, seen = [], set()
    for i in ids:
        s = summary.get(i) or {}
        document = _DOCUMENT.search(s.get("bookinfo", ""))
        if not document:
            continue
        doc_id, title = document.group(1), html.unescape(document.group(2))
        if doc_id in seen or not (needle in _stem(doc_id) or needle in title.lower()):
            continue
        seen.add(doc_id)
        accession = s.get("chapteraccessionid") or s.get("accessionid")
        sheets.append(
            {
                "title": title,
                "url": f"https://www.ncbi.nlm.nih.gov/books/{accession}/",
                "accession": accession,
                "language": _language(doc_id),
                "bookshelf_date": (s.get("pubdate") or "")[:10] or None,
            }
        )
    return sheets[:n]
