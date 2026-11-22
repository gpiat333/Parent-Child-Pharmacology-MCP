"""Validate the committed XML/CSV registry, or upload public cases to local Phoenix."""

import argparse
import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_cases():
    folder = ROOT / "eval/benchmark/datasets/mprint-v1"
    pairs = ET.parse(folder / "evaluation.xml").getroot().findall("qa_pair")
    rows = list(csv.DictReader((folder / "dataset.csv").open(encoding="utf-8-sig", newline="")))
    assert len(pairs) == len(rows) == 10
    for pair, row in zip(pairs, rows):
        assert pair.findtext("question").strip() == row["query"].strip()
        assert pair.findtext("answer").strip() == row["responses"].strip()
    assert len({r["query"] for r in rows}) == 10
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--endpoint", default="http://127.0.0.1:6062")
    args = parser.parse_args()
    rows = load_cases()
    if args.dry_run:
        print(json.dumps({"validated_cases": len(rows), "dataset": "mprint-v1"}))
    else:
        from phoenix.client import Client

        data = Client(base_url=args.endpoint).datasets.create_dataset(
            name="parent-child-mprint-v1",
            inputs=[{"query": r["query"]} for r in rows],
            outputs=[{"responses": r["responses"]} for r in rows],
        )
        print(data.id)
