"""Central configuration (env-driven so app.yaml controls everything)."""

import os
import re

from dotenv import load_dotenv

load_dotenv(override=False)


def _ident(value: str) -> str:
    # Catalog/schema names are interpolated into SQL, so validate strictly.
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise ValueError(f"Invalid identifier: {value!r}")
    return value


CATALOG = _ident(os.getenv("UC_CATALOG", "main"))
SCHEMA = _ident(os.getenv("UC_SCHEMA", "mother_child"))
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "")
USE_LAKEHOUSE = bool(WAREHOUSE_ID) and os.getenv("USE_LAKEHOUSE", "true").lower() == "true"

NCBI_EMAIL = os.getenv("NCBI_EMAIL", "you@example.gov")
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
NCBI_INTERVAL = 0.11 if NCBI_API_KEY else 0.35  # NCBI limits: 10/s with key, 3/s without

DISCLAIMER = (
    "Informational only; not medical advice. Compiled from public NIH/NLM/FDA data, which may be "
    "incomplete or out of date. Patients should talk to a clinician, pharmacist or poison control "
    "before starting, stopping or changing any medication."
)


def table(name: str) -> str:
    return f"`{CATALOG}`.`{SCHEMA}`.`{_ident(name)}`"


def index(name: str) -> str:
    return f"{CATALOG}.{SCHEMA}.{_ident(name)}"


# Process-local GET cache; upstream timestamps survive cache hits.
CACHE_TTL_SECONDS = {
    "eutils.ncbi.nlm.nih.gov": 3600,
    "www.ncbi.nlm.nih.gov": 3600,
    "dailymed.nlm.nih.gov": 3600,
    "rxnav.nlm.nih.gov": 86400,
    "clinicaltrials.gov": 3600,
    "api.reporter.nih.gov": 3600,
    "api.fda.gov": 3600,
    "www.fda.gov": 86400,
    "wsearch.nlm.nih.gov": 3600,
    "connect.medlineplus.gov": 3600,
    "www.nichd.nih.gov": 86400,
    "www.federalregister.gov": 3600,
    "api.github.com": 86400,
}
