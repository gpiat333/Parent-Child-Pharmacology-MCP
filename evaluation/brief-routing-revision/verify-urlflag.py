from pathlib import Path
import json,re
R=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20/evaluation/brief-routing-revision')
raw=json.loads((R/'chats/R12-results.json').read_text(encoding='utf-8-sig'))
answer_links=sorted(set(re.findall(r'\[[^\]]*\]\((https?://[^)\s]+)\)',raw['answer'])))
retrieval_text=json.dumps(raw['tool_calls'],ensure_ascii=False)
verified=[{'url':url,'present_in_raw_tool_calls':url in retrieval_text} for url in answer_links]
assert len(verified)==2 and all(x['present_in_raw_tool_calls'] for x in verified)
review={'case':'R12','original_provenance_pass':False,'raw_score_retained':True,'score_changed':False,'finding':'The unchanged URL regex joined two adjacent Markdown citations into one unmatched string. Both separate link targets occur in the saved tool outputs. This is a parser limitation, not a finding about claim support. The reported raw URL result remains 20/21.','links':verified}
(R/'url-parser-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
print(json.dumps(review,indent=2))
