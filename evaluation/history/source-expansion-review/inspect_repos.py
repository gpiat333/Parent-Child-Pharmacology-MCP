import concurrent.futures,json,urllib.request
from pathlib import Path
import truststore
truststore.inject_into_ssl()
B=Path(__file__).parent
repos=['GSA-TTS/cdc-places-mcp-server','GSA-TTS/mcp-server-nih-clinicaltrials','GSA-TTS/mcp-server-ncbi-eutils','GSA-TTS/mcp-server-hub-catalog','genomoncology/biomcp','cyanheads/pubmed-mcp-server','andybrandt/mcp-simple-pubmed','QuentinCody/europepmc-mcp-server','Furox-Art/literature-evidence-mcp','langli-lab/mprint-kp-data','openpharma-org/cdc-mcp']
def get(url):
 return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MCP-source-review'}),timeout=45).read()
def inspect(repo):
 out={'repo':repo,'url':'https://github.com/'+repo}
 folder=B/repo.replace('/','__');folder.mkdir(exist_ok=True)
 try:
  data=json.loads(get('https://api.github.com/repos/'+repo))
  out.update({k:data.get(k) for k in ['description','archived','pushed_at','default_branch','language','license','open_issues_count','stargazers_count']})
  branch=data['default_branch']
  tree=json.loads(get('https://api.github.com/repos/'+repo+'/git/trees/'+branch+'?recursive=1'))
  out['sha']=tree['sha'];out['files']=[x['path'] for x in tree.get('tree',[]) if x['type']=='blob']
  for name in ['README.md','LICENSE','pyproject.toml','package.json']:
   if name in out['files']:
    (folder/name).write_bytes(get('https://raw.githubusercontent.com/'+repo+'/'+out['sha']+'/'+name))
  (folder/'metadata.json').write_text(json.dumps(out,indent=2))
 except Exception as e:out['error']=type(e).__name__+': '+str(e)
 return out
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(inspect,repos))
(B/'repositories.json').write_text(json.dumps(results,indent=2))
for r in results:
 print(json.dumps({k:r.get(k) for k in ['repo','pushed_at','archived','language','error']}))
 print('license:',(r.get('license') or {}).get('spdx_id'),'files:',len(r.get('files',[])))
