"""Public NICHD HTML discovery. No controlled data or undocumented API calls."""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlencode, urljoin, urlsplit

from parent_child_pharmacology.core.http import http

BPCA = "https://www.nichd.nih.gov/research/supported/bpca/study-summaries"
DASH = "https://dash.nichd.nih.gov/explore/study"
FAQ = "https://dash.nichd.nih.gov/resource/FAQs"
NETWORKS = {
    "mfmu": "Maternal-Fetal Medicine Units (MFMU) Network",
    "neonatal": "Neonatal Research Network",
}


@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def text(self):
        return " ".join(
            " ".join(c.text() if isinstance(c, Node) else c for c in self.children).split()
        )

    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                yield from c.walk()

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()


class Tree(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node("root")
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        n = Node(tag, dict(attrs))
        self.stack[-1].children.append(n)
        if tag not in {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }:
            self.stack.append(n)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def safe_url(value, base):
    url = urljoin(base, value)
    return url if urlsplit(url).scheme == "https" and not urlsplit(url).username else None


def parse_bpca(html):
    records = {}
    for n in Tree(html).root.walk():
        if n.tag != "a":
            continue
        href = safe_url(n.attrs.get("href", ""), BPCA)
        if not href:
            continue
        if (
            "/inline-files/BPCAStudySumm" in href
            or (urlsplit(href).hostname == "pediatrictrials.org" and href.lower().endswith(".pdf"))
            or (urlsplit(href).hostname == "www.nichd.nih.gov" and "fluconazole" in href)
        ):
            if n.text():
                records[href] = {
                    "title": n.text(),
                    "url": href,
                    "evidence_type": "linked study summary or research news",
                    "content_retrieved": "index title and link only; summary document not retrieved",
                }
    if not records:
        raise ValueError("BPCA index schema changed or unavailable")
    return list(records.values())


def parse_dash(html):
    root = Tree(html).root
    counts = [n.text() for n in root.walk() if n.has_class("results-count")]
    if not counts or not re.match(r"^[\d,]+ Total Results", counts[0]):
        raise ValueError("DASH results schema changed or unavailable")
    total = int(counts[0].split()[0].replace(",", ""))
    records = []
    for card in root.walk():
        if not card.has_class("dash-data-item"):
            continue
        sid = card.attrs.get("data-study-id", "")
        links = [n for n in card.walk() if n.tag == "a" and n.attrs.get("href") == "/study/" + sid]
        if not sid.isdigit() or not links:
            raise ValueError("DASH study schema changed")
        metadata = {}
        for n in card.walk():
            if n.has_class("metadata-item") or n.has_class("field-row"):
                text = n.text()
                if ":" in text:
                    key, value = text.split(":", 1)
                    metadata[key.strip()] = value.strip()
        pubs = []
        for n in card.walk():
            if n.has_class("field-row") and n.text().startswith("Publication URLs:"):
                pubs = [safe_url(a.attrs.get("href", ""), DASH) for a in n.walk() if a.tag == "a"]
        records.append(
            {
                "study_id": sid,
                "title": links[0].text(),
                "url": "https://dash.nichd.nih.gov/study/" + sid,
                "description": metadata.get("Study Description"),
                "network": metadata.get("NICHD Research Networks and Initiatives"),
                "doi": metadata.get("DOI"),
                "source_repository": metadata.get("Source Repository"),
                "study_type": metadata.get("Study Type"),
                "topics": metadata.get("Topic"),
                "publication_urls": list(dict.fromkeys(x for x in pubs if x)),
                "data_access_note": metadata.get(
                    "Information for obtaining study data not available in DASH"
                ),
            }
        )
    if total and not records:
        raise ValueError("DASH returned total but no parseable studies")
    return records, total


def validate(query, max_results):
    query = query.strip()
    if len(query) > 200:
        raise ValueError("Query must be at most 200 characters")
    if not 1 <= max_results <= 25:
        raise ValueError("max_results must be between 1 and 25")
    return query


def envelope(source, url, results):
    return {
        "source": source,
        "url": url,
        "queried_at_utc": datetime.now(timezone.utc).isoformat(),
        "cache_note": "Public HTML may be cached for up to one hour.",
        "results": results,
        "caveat": "Discovery results are not clinical recommendations. No match does not establish absence of evidence or safety.",
    }


async def search_bpca(query="", max_results=10):
    query = validate(query, max_results)
    response = await http.request("GET", BPCA, ttl=3600)
    records = parse_bpca(response.text)
    tokens = re.findall(r"[a-z0-9]+", query.lower())
    matches = [
        r for r in records if all(t in re.findall(r"[a-z0-9]+", r["title"].lower()) for t in tokens)
    ]
    out = envelope("live:nichd-bpca-index", BPCA, matches[:max_results])
    out.update(
        index_records=len(records),
        matching_records=len(matches),
        results_truncated=len(matches) > max_results,
        search_scope="Titles linked on the NICHD BPCA study summaries page, including featured PTN summaries. Not full-text PDF search or all PTN studies.",
    )
    return out


async def search_dash(query="", network="any", max_results=10, page=0):
    query = validate(query, max_results)
    if network not in {"any", *NETWORKS}:
        raise ValueError("network must be any, mfmu, or neonatal")
    if not 0 <= page <= 100:
        raise ValueError("page must be between 0 and 100")
    # Search the public form; network membership is then verified against source metadata.
    params = {"search": query, "page": page, "per_page": 100}
    if network != "any":
        params["network[" + NETWORKS[network] + "]"] = NETWORKS[network]
    response = await http.request("GET", DASH, params=params, ttl=3600)
    records, total = parse_dash(response.text)
    matches = [
        r
        for r in records
        if network == "any" or NETWORKS[network].lower() in (r["network"] or "").lower()
    ]
    out = envelope("live:nichd-dash", DASH + "?" + urlencode(params), matches[:max_results])
    out.update(
        access_url=FAQ,
        access_note="Public metadata only. Underlying data require DASH or the source repository's access process; no participant data were accessed.",
        network_filter=network,
        page=page,
        upstream_total_results=total,
        upstream_page_records=len(records),
        matching_records_on_page=len(matches),
        results_truncated=len(matches) > max_results or total > (page + 1) * 100,
        next_page=page + 1 if total > (page + 1) * 100 else None,
        search_scope="DASH public search results on this page; network filter uses explicit network metadata, not inferred membership. Results are study descriptions, not a systematic review or a current recruiting-trial list.",
    )
    return out
