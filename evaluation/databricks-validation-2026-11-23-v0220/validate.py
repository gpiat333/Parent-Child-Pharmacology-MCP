# Databricks notebook source
import tempfile, zipfile, hashlib, pathlib, subprocess, sys, os, json
work=pathlib.Path(tempfile.mkdtemp(prefix='mcp-template-tests-'))
archive=work/'frozen-tests.zip'
archive.write_bytes(b''.join(p.read_bytes() for p in sorted(pathlib.Path('/Workspace/Users/gabriela.piatkowski@nih.gov/mcp-tests-v0220-183257').glob('frozen-tests.part*'))))
assert hashlib.sha256(archive.read_bytes()).hexdigest()=="b7078866004883d54f01cf99cdfdbbb3ac9cf6ea3be31d3225d73b0a34a9415c"
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
result={'archive_sha256':"b7078866004883d54f01cf99cdfdbbb3ac9cf6ea3be31d3225d73b0a34a9415c",'runtime':'Databricks serverless notebook; isolated Python 3.13 uv environment','returncode':test.returncode,'counts':totals,'stdout':test.stdout[-9000:],'stderr':test.stderr[-2000:]}
print(json.dumps(result))
assert test.returncode==0 and not any(totals[k] for k in ['failures','errors','skipped']),json.dumps(result)
dbutils.notebook.exit(json.dumps(result))
