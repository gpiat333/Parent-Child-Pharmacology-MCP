from pathlib import Path
import json
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/brief-paraphrase-revision'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
S=read(R/'summary.json');findings=read(R/'grading-review.json')['findings']
notes=read(W/'technical-notes.json') if (W/'technical-notes.json').exists() else {}
parts=['# Technical review of diagnostic grades',
'Raw model scores are retained without overrides. This review checks the interpretation of the scores and selected answer text; it is not independent clinical adjudication.',
'## Meaning and scope',
'Fidelity checks source claims against the bounded captured evidence pool. Task fulfillment checks the specified lookup or output requirements. They are independent. A source-supported answer can omit a requirement; an honest inability to retrieve current information can leave a task incomplete. Not-assessable fidelity is excluded from fidelity rates. A URL match does not establish claim support.',
'The same known questions and grader v2 prompt were used. Each arm retains one completed response. Only MCP has retrieval, enforced workflows and fixed notices. The paired runner uses a shorter prompt than the chat companion. These conditions do not establish isolated model ability, clinical accuracy or general superiority.',
'## Current negative grades']
for f in findings:
 cid=f['case'];arm=f.get('arm','chat');key=arm+':'+cid
 parts.append('### '+cid+' — '+arm)
 if f['type']!='diagnostic_model_finding':
  parts.append('Deterministic check: '+f['type']+'. Inspect the retained capture and chat-checks.json.');continue
 parts.append(f"Raw fidelity: **{f['fidelity_status']}**. Raw task fulfilled: **{f['task_fulfilled']}**.")
 parts.append('Grader rationale (unadjudicated):\n\n> '+f['rationale'].replace('\n','\n> '))
 if key in notes:parts.append('Technical observation: '+notes[key])
 else:parts.append('No independent override is applied. The rationale is a model judgment and may require source or clinician review.')
 capture=f'chats/{cid}-results.json' if arm=='chat' else f'paired-final/{cid}-{arm}.json'
 grade=f'chat-judgments/{cid}.json' if arm=='chat' else f'paired-final/{cid}-{arm}-judge.json'
 parts.append(f'[Captured answer and tool evidence]({capture}) · [Raw grade]({grade})')
parts+=['## Historical figures in the question',
'The preceding Databricks run had 19/21 fidelity passes and 19/21 fulfilled research tasks. Those were separate counts and did not identify the same two failures. Its paired task result of MCP 7/7 versus plain 0/7 concerned seven source-lookup tasks without retrieval tools in the plain arm. Zero tasks fulfilled was not a finding that every answer was false. The current totals are in summary.json and REPORT.md; older records are preserved.',
'## Routing regression',
'The original “Give me a pregnancy evidence brief for lamotrigine” question completed with medication_evidence_brief as its first evidence call. Twelve direct deployed preflight checks cover positive variants, negation, incidental mention and overriding stops. They are separate from the 28-case benchmark and 42 final MLflow rows. The matcher remains a narrow English heuristic, not exhaustive language understanding.',
'No clinician adjudication occurred. Raw negative scores and all completed answers remain unchanged.']
(R/'TECHNICAL_REVIEW.md').write_text('\n\n'.join(parts)+'\n',encoding='utf-8')
print('Technical review preserves every negative grade and distinguishes manual observations.')
