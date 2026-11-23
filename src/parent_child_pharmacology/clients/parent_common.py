"""Bounded public-source discovery for parents; no submissions or patient records."""

from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit

from parent_child_pharmacology.core.safety import contains_identifiers

RECALLS = "https://api.fda.gov/drug/enforcement.json"
RECALL_HELP = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-recalls"
ALERTS = "https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications"
REGISTRIES = (
    "https://www.fda.gov/consumers/pregnancy-exposure-registries/list-pregnancy-exposure-registries"
)
DIRECTORIES = [
    {
        "title": "NIH public involvement",
        "url": "https://www.nih.gov/about-nih/get-involved-nih/public-involvement-nih",
    },
    {
        "title": "FDA patient-focused drug development",
        "url": "https://www.fda.gov/drugs/development-approval-process-drugs/cder-patient-focused-drug-development",
    },
]


def now():
    return datetime.now(timezone.utc).isoformat()


def term(value, allow_empty=False):
    value = value.strip()
    if (not value and not allow_empty) or len(value) > 160 or contains_identifiers(value):
        raise ValueError(
            "Use a short, non-identifying medicine, condition or topic; no medical histories or contact details."
        )
    return value


def limit(n):
    return max(1, min(n, 20))


def links(node, base):
    out = []
    for a in node.walk():
        if a.tag != "a":
            continue
        url = urljoin(base, a.attrs.get("href", ""))
        if urlsplit(url).scheme in ("https", "http"):
            out.append({"title": a.text(), "url": url})
    return out
