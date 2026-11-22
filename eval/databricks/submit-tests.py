import argparse
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--workspace-dir", required=True)
parser.add_argument("--output", type=Path, required=True)
a = parser.parse_args()
P = Path(__file__).resolve().parents[2]
R = a.output.resolve()
R.mkdir(parents=True, exist_ok=False)
W = R
CLI = os.environ.get("DATABRICKS_CLI_PATH", "databricks")
profile = os.environ["DATABRICKS_CONFIG_PROFILE"]
base = a.workspace_dir.rstrip("/")
if not base.startswith(("/Users/", "/Shared/")) or ".." in base.split("/"):
    raise ValueError("Choose a new absolute workspace directory under /Users or /Shared")
archive = W / "frozen-tests.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    for root in ["src", "tests", "chat-client"]:
        for f in (P / root).rglob("*"):
            if f.is_file() and "__pycache__" not in str(f) and f.suffix != ".pyc":
                z.write(f, f.relative_to(P))
    for name in [
        "main.py",
        "pyproject.toml",
        "uv.lock",
        "server/requirements.lock",
        "README.md",
        "evaluation/program-safety-revision/cases.json",
        "evaluation/brief-routing-revision/chats/R12-results.json",
    ]:
        z.write(P / name, name)
sha = hashlib.sha256(archive.read_bytes()).hexdigest()
notebook = (
    """# Databricks notebook source
import tempfile, zipfile, hashlib, pathlib, subprocess, sys, os, json
work=pathlib.Path(tempfile.mkdtemp(prefix='mcp-template-tests-'))
archive=work/'frozen-tests.zip'
archive.write_bytes(b''.join(p.read_bytes() for p in sorted(pathlib.Path('/Workspace"""
    + base
    + '''').glob('frozen-tests.part*'))))
assert hashlib.sha256(archive.read_bytes()).hexdigest()=="'''
    + sha
    + '''"
with zipfile.ZipFile(archive) as z:z.extractall(work)
# Isolated ephemeral venv uses the project's exact uv lock and Python 3.13.
bootstrap=subprocess.run([sys.executable,'-m','pip','install','--target',str(work/'tooling'),'uv==0.13.9'],capture_output=True,text=True)
assert bootstrap.returncode==0,bootstrap.stderr[-2500:]
import urllib.request,tarfile,platform
url='https://github.com/PowerShell/PowerShell/releases/download/v7.7.0/'
arch={'aarch64':'arm64','x86_64':'x64'}[platform.machine()]
filename='powershell-7.7.0-linux-'+arch+'.tar.gz'
# SHA256 published on the official PowerShell v7.7.0 GitHub release asset.
expected={'arm64':'e59c89776eaa59790d44b3edd14277435225ab08b6e7603763101b89de83d935','x64':'c89d9c682d2c403dfe726f3df948e359675235a5bd6fab535776de69729ca0cb'}[arch]
download=work/filename
urllib.request.urlretrieve(url+filename,download)
assert hashlib.sha256(download.read_bytes()).hexdigest()==expected
pwsh=work/'powershell';pwsh.mkdir()
with tarfile.open(download) as t:t.extractall(pwsh,filter='data')
(pwsh/'pwsh').chmod(0o755)
env=dict(os.environ,PYTHONPATH=str(work/'tooling'),USE_LAKEHOUSE='false',MCP_TRANSPORT='stdio',PATH=str(pwsh)+os.pathsep+os.environ['PATH'],NO_COLOR='1')
uv=[sys.executable,'-m','uv']
install=subprocess.run(uv+['sync','--locked','--group','dev','--python','3.13'],cwd=work,env=env,capture_output=True,text=True)
assert install.returncode==0,install.stderr[-2500:]
env['PYTHONPATH']=str(work/'src')
test=subprocess.run([str(work/'.venv/bin/python'),'-m','pytest','tests','-q','--junitxml='+str(work/'results.xml')],cwd=work,env=env,capture_output=True,text=True,timeout=1200)
import xml.etree.ElementTree as ET
root=ET.parse(work/'results.xml').getroot()
totals={k:sum(int(s.attrib.get(k,0)) for s in root.findall('testsuite')) for k in ['tests','failures','errors','skipped']}
result={'archive_sha256':"'''
    + sha
    + """",'runtime':'Databricks serverless notebook; isolated Python 3.13 uv environment','returncode':test.returncode,'counts':totals,'stdout':test.stdout[-9000:],'stderr':test.stderr[-2000:]}
print(json.dumps(result))
assert test.returncode==0 and not any(totals[k] for k in ['failures','errors','skipped']),json.dumps(result)
dbutils.notebook.exit(json.dumps(result))
"""
)
(W / "validate.py").write_text(notebook, encoding="utf-8")


def call(*args):
    r = subprocess.run(
        [CLI, *args, "--profile", profile, "--output", "json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if r.returncode:
        raise RuntimeError(r.stderr[:2500])
    return json.loads(r.stdout) if r.stdout.strip() else {}


call("workspace", "mkdirs", base)
blob = archive.read_bytes()
for index, start in enumerate(range(0, len(blob), 20_000_000)):
    part = W / ("frozen-tests.part" + str(index))
    part.write_bytes(blob[start : start + 20_000_000])
    call("workspace", "import", base + "/" + part.name, "--file", str(part), "--format", "RAW")
call(
    "workspace",
    "import",
    base + "/validate",
    "--file",
    str(W / "validate.py"),
    "--format",
    "SOURCE",
    "--language",
    "PYTHON",
)
spec = {
    "run_name": "MCP .12 frozen source unit tests - no App deployment",
    "timeout_seconds": 1800,
    "tasks": [
        {
            "task_key": "frozen_source_tests",
            "notebook_task": {"notebook_path": base + "/validate", "source": "WORKSPACE"},
            "environment_key": "tests",
        }
    ],
    "environments": [{"environment_key": "tests", "spec": {"client": "4"}}],
}
(W / "submit.json").write_text(json.dumps(spec), encoding="utf-8")
result = call("jobs", "submit", "--json", "@" + str(W / "submit.json"), "--no-wait")
(R / "databricks-job-submitted.json").write_text(
    json.dumps(
        {
            "job": result,
            "source_sha256": sha,
            "workspace_path": base,
            "bytes": archive.stat().st_size,
            "spec": spec,
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(json.dumps(result))
