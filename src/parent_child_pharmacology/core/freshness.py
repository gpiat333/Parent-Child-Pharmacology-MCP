"""Freshness of bundled (non-live) data, so users can see when a saved copy may be out of date.

MPRINT is the only bundled dataset; every other source is fetched live. Each MPRINT result
carries an offline freshness block (no network call). The snapshot resource and the
maintainer script additionally compare the bundled revision with the upstream repository.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "mc/data/mprint-manifest.json"
UPSTREAM_REPO = "langli-lab/mprint-kp-data"
UPSTREAM_COMMITS_PAGE = f"https://github.com/{UPSTREAM_REPO}/commits"
UPSTREAM_COMMITS_API = f"https://api.github.com/repos/{UPSTREAM_REPO}/commits"
# Upstream has changed rarely; a six-month-old copy should be re-checked before relying on it.
CHECK_AFTER_DAYS = 180


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def mprint_freshness(now=None):
    """Offline freshness block attached to every MPRINT result."""
    m = _manifest()
    saved = datetime.fromisoformat(m["retrieved_at_utc"])
    age = max(0, ((now or datetime.now(timezone.utc)) - saved).days)
    due = age >= CHECK_AFTER_DAYS
    revision = m["revision"]
    return {
        "dataset": "MPRINT",
        "mode": "saved_copy",
        "saved_on": saved.date().isoformat(),
        "age_days": age,
        "revision": revision,
        "status": "check_recommended" if due else "within_check_window",
        "check_after_days": CHECK_AFTER_DAYS,
        "how_to_check": f"Compare revision {revision[:7]} with the latest commit at {UPSTREAM_COMMITS_PAGE}, "
        "or read the parent-child://mprint-snapshot resource, which checks automatically.",
        "display_note": (
            f"MPRINT results come from a saved copy dated {saved.date().isoformat()} "
            f"(revision {revision[:7]}), {age} days old. "
            + (
                "It is past the recommended check date; newer MPRINT data may exist."
                if due
                else "Newer MPRINT data may exist; check the source before relying on it."
            )
        ),
    }


def compare_upstream(latest_sha, latest_date, bundled_revision):
    """Pure comparison so it can be tested without network access."""
    if not latest_sha:
        return "unable_to_check"
    return "up_to_date" if latest_sha == bundled_revision else "newer_upstream_data_available"


async def check_upstream():
    """Ask the upstream repository for its latest commit (cached for a day)."""
    from .http import http

    bundled = _manifest()["revision"]
    out = {"checked_url": UPSTREAM_COMMITS_PAGE, "bundled_revision": bundled}
    try:
        response = await http.request(
            "GET",
            UPSTREAM_COMMITS_API,
            params={"per_page": 1},
            ttl=86400,
        )
        latest = response.json()[0]
        sha, date = latest["sha"], latest["commit"]["committer"]["date"]
        out.update(latest_upstream_revision=sha, latest_upstream_date=date)
    except Exception as e:  # a failed check must never read as "up to date"
        sha, date = None, None
        out["error"] = type(e).__name__
    out["status"] = compare_upstream(sha, date, bundled)
    out["meaning"] = {
        "up_to_date": "The saved copy matches the latest upstream data.",
        "newer_upstream_data_available": "MPRINT has published changes since this copy was saved. "
        "Results may be missing newer studies until the snapshot is rebuilt.",
        "unable_to_check": "The upstream repository could not be reached. Freshness is unknown, not confirmed.",
    }[out["status"]]
    return out
