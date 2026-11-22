"""Reproduce an evaluation into a new, immutable evidence directory."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)
for optional in ["AGENT_MODEL", "JUDGE_MODEL", "MCP_EVAL_ENDPOINT", "DATABRICKS_CLI_PATH"]:
    if not os.environ.get(optional):
        os.environ.pop(optional, None)
parser = argparse.ArgumentParser()
parser.add_argument(
    "phase", choices=["prepare", "chats", "paired", "grade", "mlflow", "verify", "inspector"]
)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--suite", choices=["research", "stops", "paired"])
args = parser.parse_args()
out = args.output.resolve()
os.environ["MCP_REPO_ROOT"] = str(ROOT)
os.environ.setdefault("AGENT_MODEL", "system.ai.gpt-5-6-luna")
os.environ.setdefault("MCP_EVAL_ENDPOINT", "http://127.0.0.1:8000/mcp")
if args.phase == "prepare":
    if out.exists():
        raise SystemExit("Choose a NEW output directory; historical evidence is never overwritten.")
    shutil.copytree(
        ROOT / "eval/harness", out, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache")
    )
    files = [
        *(
            p
            for p in ROOT.joinpath("src").rglob("*")
            if "__pycache__" not in p.parts and p.suffix != ".pyc"
        ),
        *ROOT.joinpath("chat-client").glob("*"),
        *(
            p
            for p in ROOT.joinpath("eval/phoenix").rglob("*")
            if "__pycache__" not in p.parts and p.suffix in {".py", ".txt", ".yaml"}
        ),
        *ROOT.joinpath("eval/benchmark/datasets/mprint-v1").glob("*"),
        *(
            p
            for p in ROOT.joinpath("eval/harness").rglob("*")
            if "__pycache__" not in p.parts and p.suffix != ".pyc"
        ),
        ROOT / "main.py",
        ROOT / "pyproject.toml",
        ROOT / "uv.lock",
        ROOT / "server/requirements.lock",
    ]
    hashes = {
        str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in files
        if p.is_file()
    }
    design = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "version": "0.14.0",
        "policy": "2026-11-22.14",
        "source_sha256": hashes,
        "model": os.environ["AGENT_MODEL"],
        "judge_model": os.getenv("JUDGE_MODEL", os.environ["AGENT_MODEL"]),
        "endpoint": os.environ["MCP_EVAL_ENDPOINT"],
        "method": "Fresh single captures on 28 known cases and seven paired cases. Unchanged judge prompt with v3.1 validation that rejects footer-only negative findings; R08 criterion clarified to accept elapsed/past-listed deadlines without claiming verified portal closure. All questions and other criteria unchanged. Same-family diagnostic judgments, no clinician review. Fixed MPRINT benchmark questions/answers unchanged; v2 runner uses supported none reasoning, joined candidate metadata and bounded arithmetic. Local MCP; Databricks models/tracking. No deployment. Failed attempts retained; no answer selection by score.",
    }
    (out / "run-design.json").write_text(json.dumps(design, indent=2), encoding="utf-8")
    print(out)
    raise SystemExit(0)
if not (out / "run-design.json").is_file():
    raise SystemExit("Run prepare first.")
design = json.loads((out / "run-design.json").read_text())
changed = [
    p
    for p, h in design["source_sha256"].items()
    if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h
]
if changed:
    raise SystemExit("Frozen source changed: " + ", ".join(changed))
if args.phase == "chats":
    cmd = [shutil.which("pwsh") or "pwsh", "-NoProfile", "-File", str(out / "run-chats.ps1")]
else:
    script = {
        "paired": "paired_evaluation.py",
        "grade": "score_current.py",
        "mlflow": "run-mlflow.py",
        "verify": "verify-mlflow.py",
        "inspector": "inspect-mcp.py",
    }[args.phase]
    cmd = [sys.executable, "-X", "utf8", str(out / script)]
    if args.phase == "paired":
        cmd += ["--phase", "generate"]
    if args.phase == "mlflow":
        cmd += ["--phase", args.suite or "research"]
    if args.phase == "verify":
        cmd += [args.suite or "research"]
raise SystemExit(subprocess.call(cmd, cwd=ROOT))
