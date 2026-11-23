"""Maintainer check: is the bundled MPRINT snapshot behind its upstream repository?

Exit codes: 0 up to date, 1 newer upstream data available, 2 unable to check.
Run with: uv run python scripts/check_mprint_freshness.py
"""

import asyncio
import json
import sys

from parent_child_pharmacology.core.freshness import check_upstream, mprint_freshness


def main():
    result = {"bundled": mprint_freshness(), "upstream": asyncio.run(check_upstream())}
    print(json.dumps(result, indent=2))
    status = result["upstream"]["status"]
    if status == "newer_upstream_data_available":
        print("\nMPRINT has newer data. Rebuild the snapshot and update mprint-manifest.json.")
        return 1
    return 0 if status == "up_to_date" else 2


if __name__ == "__main__":
    sys.exit(main())
