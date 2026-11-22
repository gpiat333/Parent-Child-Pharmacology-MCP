from pathlib import Path
import json
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
for name in ['policy.json','output_notices.json']:
 p=P/'server/core'/name
 data=json.loads(p.read_text(encoding='utf-8-sig'));data['version']='2026-11-21.10'
 if name=='output_notices.json':
  data['abstract_coverage']={
   'counts':'PubMed abstract coverage: abstract text was retrieved for {found} of {requested} requested PMIDs.',
   'without_abstract_pmids':'No abstract text was returned for PMID(s): {ids}.',
   'unreturned_pmids':'No article record was returned for PMID(s): {ids}.',
   'failed_pmids':'The abstract request failed for PMID(s): {ids}; abstract availability is unknown.',
   'no_records':'No PubMed records were retrieved in this bounded search, so no abstracts were evaluated.',
   'search_failed':'A PubMed literature search failed; additional abstract coverage could not be verified.',
   'limit':'Missing abstract text is a retrieval limitation, not evidence that a study or research does not exist. Titles alone are not outcome evidence.'}
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=P/'chat-client/test-mcp-chat.ps1';s=p.read_text(encoding='utf-8-sig');old='-Blocked:$policyBlocked)';assert old in s
p.write_text(s.replace(old,'-Blocked:$policyBlocked -ToolCalls $trace.ToArray())'),encoding='utf-8')
p=P/'chat-client/exposure-presentation-instructions.txt'
with p.open('a',encoding='utf-8') as f:
 f.write('\nPreserve the PubMed abstract_coverage contract: explicitly disclose records with no abstract text, unreturned records, and failed abstract lookups. These are retrieval limitations, not evidence that research does not exist. Never describe study outcomes from a title alone. If a later lookup supplies the abstract, use the updated coverage; do not invent missing abstracts when no lookup was performed.\n')
print('Application policy .10; shared abstract-disclosure templates and client contract written.')
