"""Build the bundled LactMed snapshot from NCBI's official Bookshelf bulk package.

Usage: uv run python scripts/build_lactmed_snapshot.py [path/to/lactmed_NBK501922.tar.gz]
Without a path, the package is downloaded from the NCBI literature archive (litarch).
Records keep their section text with LactMed's own citation markers, e.g. [54], and a
reference list with PubMed IDs. LactMed is a U.S. government work (NICHD/NLM).
"""

import hashlib
import json
import re
import sqlite3
import sys
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

PACKAGE_URL = "https://ftp.ncbi.nlm.nih.gov/pub/litarch/90/6c/lactmed_NBK501922.tar.gz"
FILE_LIST_URL = "https://ftp.ncbi.nlm.nih.gov/pub/litarch/file_list.csv"
DATA = Path(__file__).resolve().parents[1] / "src/parent_child_pharmacology/mc/data"
HEADINGS = {
    "Summary of Use during Lactation",
    "Drug Levels",
    "Effects in Breastfed Infants",
    "Effects on Lactation and Breastmilk",
    "Alternate Drugs to Consider",
}


def _clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def _text(element):
    """Readable text of an element; nested section titles stay as inline labels."""
    parts = []
    for child in element:
        if child.tag == "title":
            continue
        if child.tag == "sec":
            title = _clean("".join(child.findtext("title") or ""))
            body = _text(child)
            parts.append(f"{title} {body}" if title else body)
        else:
            parts.append(_clean("".join(child.itertext())))
    return _clean(" ".join(p for p in parts if p))


def parse_record(xml_bytes):
    root = ET.fromstring(xml_bytes)
    title_el = root.find(".//book-part-meta//title")
    if title_el is None:
        title_el = root.find(".//title")
    title = _clean("".join(title_el.itertext())) if title_el is not None else ""
    revised = root.find(".//date[@date-type='revised']")
    revised_on = None
    if revised is not None:
        y, m, d = (revised.findtext(k) for k in ("year", "month", "day"))
        if y:
            revised_on = f"{y}-{(m or '01').zfill(2)}-{(d or '01').zfill(2)}"
    sections = {}
    for sec in root.iter("sec"):
        heading = _clean(sec.findtext("title"))
        if heading in HEADINGS and heading not in sections:
            sections[heading] = _text(sec)
    references = []
    for ref in root.iter("ref"):
        citation = ref.find("mixed-citation")
        if citation is None:
            citation = ref.find("element-citation")
        for etal in ref.iter("etal"):
            etal.text = "et al"
        pmid = ref.findtext(".//pub-id[@pub-id-type='pmid']")
        doi = ref.findtext(".//pub-id[@pub-id-type='doi']")
        text = _clean("".join(citation.itertext())) if citation is not None else ""
        if pmid:
            text = _clean(text.replace(pmid, "")).rstrip(". ") + "."
        references.append(
            {
                "number": _clean(ref.findtext("label")) or None,
                "citation": text,
                "pmid": _clean(pmid) or None,
                "doi": _clean(doi) or None,
            }
        )
    return {
        "title": title,
        "revised_on": revised_on,
        "sections": sections,
        "references": references,
    }


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if path is None:
        path = Path("lactmed_NBK501922.tar.gz")
        urllib.request.urlretrieve(PACKAGE_URL, path)
    with urllib.request.urlopen(urllib.request.Request(PACKAGE_URL, method="HEAD")) as r:
        published = parsedate_to_datetime(r.headers["Last-Modified"]).astimezone(timezone.utc)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    out = DATA / "lactmed.sqlite"
    out.unlink(missing_ok=True)
    con = sqlite3.connect(out)
    con.execute(
        "CREATE TABLE records (stem TEXT PRIMARY KEY, title TEXT, revised_on TEXT, payload BLOB)"
    )
    count = 0
    with tarfile.open(path) as tar:
        for member in tar:
            if not member.name.endswith(".nxml"):
                continue
            record = parse_record(tar.extractfile(member).read())
            stem = Path(member.name).stem
            payload = zlib.compress(json.dumps(record, ensure_ascii=False).encode(), 9)
            con.execute(
                "INSERT INTO records VALUES (?, ?, ?, ?)",
                (stem, record["title"], record["revised_on"], payload),
            )
            count += 1
    con.commit()
    con.execute("VACUUM")
    con.close()
    manifest = {
        "dataset": "LactMed (Drugs and Lactation Database)",
        "publisher": "National Institute of Child Health and Human Development (NICHD); hosted by NLM NCBI Bookshelf",
        "package_url": PACKAGE_URL,
        "file_list_url": FILE_LIST_URL,
        "package_published_utc": published.isoformat(),
        "package_sha256": sha,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "record_count": count,
        "license": "U.S. government work; public domain unless a record states otherwise (see package license.txt).",
    }
    (DATA / "lactmed-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
