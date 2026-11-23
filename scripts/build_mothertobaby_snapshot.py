"""Build the bundled MotherToBaby fact sheet snapshot from NCBI's official Bookshelf package.

Usage: uv run python scripts/build_mothertobaby_snapshot.py [path/to/mtb_NBK582980.tar.gz]
Fact sheets are (c) OTIS and licensed CC BY-NC-ND 3.0: text is stored and returned
verbatim with attribution; answers are never shortened or reworded.
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

PACKAGE_URL = "https://ftp.ncbi.nlm.nih.gov/pub/litarch/18/f4/mtb_NBK582980.tar.gz"
DATA = Path(__file__).resolve().parents[1] / "src/parent_child_pharmacology/mc/data"


def _clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def _join(element):
    return _clean(" ".join(_clean("".join(p.itertext())) for p in element.iter("p")))


def parse_sheet(xml_bytes):
    root = ET.fromstring(xml_bytes)
    title_el = root.find(".//book-part-meta//title")
    copyright_el = root.find(".//copyright-statement")
    preamble = root.find(".//question-preamble")
    qa = []
    for wrap in root.iter("question-wrap"):
        question, answer = wrap.find("question"), wrap.find("answer")
        if question is not None and answer is not None:
            qa.append({"question": _join(question), "answer": _join(answer)})
    return {
        "title": _clean("".join(title_el.itertext())) if title_el is not None else "",
        "copyright": _clean("".join(copyright_el.itertext())) if copyright_el is not None else None,
        "preamble": _join(preamble) if preamble is not None else None,
        "qa": qa,
        "reference_count": sum(1 for _ in root.iter("ref")),
    }


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("mtb_NBK582980.tar.gz")
    if len(sys.argv) <= 1:
        urllib.request.urlretrieve(PACKAGE_URL, path)
    with urllib.request.urlopen(urllib.request.Request(PACKAGE_URL, method="HEAD")) as r:
        published = parsedate_to_datetime(r.headers["Last-Modified"]).astimezone(timezone.utc)
    out = DATA / "mothertobaby.sqlite"
    out.unlink(missing_ok=True)
    con = sqlite3.connect(out)
    con.execute(
        "CREATE TABLE sheets (doc_id TEXT PRIMARY KEY, title TEXT, language TEXT, payload BLOB)"
    )
    count = 0
    with tarfile.open(path) as tar:
        for member in tar:
            if not member.name.endswith(".nxml"):
                continue
            doc_id = Path(member.name).stem
            sheet = parse_sheet(tar.extractfile(member).read())
            if not sheet["qa"]:
                continue
            language = {"en": "en", "sp": "es"}.get(doc_id.rsplit("-", 1)[-1], "unknown")
            payload = zlib.compress(json.dumps(sheet, ensure_ascii=False).encode(), 9)
            con.execute(
                "INSERT INTO sheets VALUES (?, ?, ?, ?)",
                (doc_id, sheet["title"], language, payload),
            )
            count += 1
    con.commit()
    con.execute("VACUUM")
    con.close()
    manifest = {
        "dataset": "MotherToBaby | Fact Sheets",
        "publisher": "Organization of Teratology Information Specialists (OTIS), a nonprofit; distributed by NLM NCBI Bookshelf",
        "package_url": PACKAGE_URL,
        "package_published_utc": published.isoformat(),
        "package_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "sheet_count": count,
        "license": "CC BY-NC-ND 3.0 (https://creativecommons.org/licenses/by-nc-nd/3.0/). Verbatim, attributed, noncommercial use only.",
    }
    (DATA / "mothertobaby-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
