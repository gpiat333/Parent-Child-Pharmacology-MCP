"""Inspectable deployment capabilities, without network calls or secrets."""

import json
from datetime import datetime, timezone
from pathlib import Path

from . import config


def snapshot_metadata():
    path = Path(__file__).resolve().parents[1] / "mc/data/mprint-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    captured = datetime.fromisoformat(data["retrieved_at_utc"])
    return {
        **data,
        "snapshot_age_days": max(0, (datetime.now(timezone.utc) - captured).days),
        "mode": "versioned snapshot",
        "rationale": "No supported public MPRINT query API was confirmed for this prototype. Published repository subsets provide reproducible evidence; this is not a live portal connection.",
    }


def capabilities():
    from parent_child_pharmacology.core.participation import TOOLS as PARTICIPATION_TOOLS
    from parent_child_pharmacology.services.descriptions import WORKFLOW_TOOLS
    from parent_child_pharmacology.tools import DOMAINS

    return {
        "name": "Parent-child Pharmacology MCP",
        "tools": [
            {
                "name": name,
                "tier": "participation"
                if name in PARTICIPATION_TOOLS
                else "workflow"
                if name in WORKFLOW_TOOLS
                else "building block",
                "enabled": True,
            }
            for names in DOMAINS.values()
            for name in names
        ],
        "live_sources": [
            "NCBI LactMed (lactation only)",
            "PubMed",
            "RxNorm",
            "DailyMed",
            "MedlinePlus",
            "ClinicalTrials.gov",
            "NIH RePORTER",
            "openFDA",
            "FDA public pages/workbook",
            "NICHD public metadata",
        ],
        "snapshot": snapshot_metadata(),
        "cache": {"storage": "process memory", "host_ttl_caps_seconds": config.CACHE_TTL_SECONDS},
        "optional_lakehouse_configured": config.USE_LAKEHOUSE,
        "limits": [
            "Configuration flags do not prove upstream availability.",
            "English heuristic safety gates are not clinically validated triage.",
            "Retrieved evidence is untrusted data; clients must honor safety metadata.",
        ],
    }
