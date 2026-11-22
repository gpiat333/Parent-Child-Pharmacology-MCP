"""One fresh answer per fixed snapshot question; exact-match scoring, no model judge."""

import argparse
import hashlib
import json
import threading
from pathlib import Path

from agent import ParentChildPharmacologyAgent
from create_dataset import ROOT, load_cases


def exact_match(output, expected):
    return str(output).strip() == str(expected["responses"]).strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-directory", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:6062")
    args = parser.parse_args()
    from phoenix.client import Client
    rows = load_cases()
    agent = ParentChildPharmacologyAgent(args.evidence_directory)
    client = Client(base_url=args.endpoint)
    dataset = client.datasets.create_dataset(name="parent-child-mprint-v1-" + args.evidence_directory.name, inputs=[{"query": r["query"]} for r in rows], outputs=[{"responses": r["responses"]} for r in rows])
    identifiers = {r["query"]: f"B{i:02}" for i, r in enumerate(rows, 1)}
    gateway_lock = threading.Lock()

    def task(input):
        # Phoenix may dispatch examples concurrently; serialize gateway use to
        # respect the prototype workspace's quota, without selecting by score.
        with gateway_lock:
            return agent.run(identifiers[input["query"]], input["query"])

    experiment = client.experiments.run_experiment(dataset=dataset, task=task, evaluators=[exact_match], experiment_name="MPRINT fixed snapshot v1", experiment_description="Single fresh tool-enabled answers. Independent read-only question exploration; exact reference matching, no clinical validity claim.", repetitions=1, retries=0)
    readback = client.experiments.get_experiment(experiment_id=experiment["experiment_id"])
    captures = [json.loads((agent.output / f"B{i:02}.json").read_text(encoding="utf-8")) for i in range(1, 11)]
    results = [{"id": c["id"], "completed": c["completed"], "expected": r["responses"], "actual": c["answer"], "exact_match": exact_match(c["answer"], r), "tool_calls": len(c["calls"])} for c, r in zip(captures, rows)]
    files = [*Path(__file__).parent.rglob("*.py"), *Path(__file__).parent.rglob("*.txt"), *ROOT.joinpath("eval/benchmark/datasets/mprint-v1").glob("*")]
    summary = {"cases": 10, "exact_match_passes": sum(r["exact_match"] for r in results), "completed": sum(r["completed"] for r in results), "dataset_id": dataset.id, "experiment_id": experiment["experiment_id"], "phoenix_readback": bool(readback), "results": results, "method_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}, "limitations": "Known fixed-snapshot benchmark, small sample, exact format, two evidence tools; not clinical validation, not a whole-toolset or plain-model comparison. Existing development chat grades remain separate."}
    (agent.output / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (agent.output / "phoenix-readback.json").write_text(json.dumps(readback, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["cases", "exact_match_passes", "completed", "experiment_id"]}))
