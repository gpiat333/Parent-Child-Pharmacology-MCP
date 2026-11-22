from pathlib import Path
import json
W=Path(__file__).parent
P=Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R=P/'evaluation/report-context-revision'
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
positive_notes=[]
negative_keys={f.get('arm','chat')+':'+f['case'] for f in findings}
for key,note in notes.items():
 if key in negative_keys:continue
 arm,cid=key.split(':',1)
 grade=f'chat-judgments/{cid}.json' if arm=='chat' else f'paired-final/{cid}-{arm}-judge.json'
 capture=f'chats/{cid}-results.json' if arm=='chat' else f'paired-final/{cid}-{arm}.json'
 if (R/grade).exists():positive_notes.append(f'### {cid} — {arm}\n\n{note}\n\n[Captured answer]({capture}) · [Raw grade]({grade})')
if positive_notes:parts+=['## Technical observations on passing grades',*positive_notes]
parts+=['## Historical figures in the question',
'The .5 run cited in the question had 21/21 fidelity passes and 18/21 fulfilled research tasks, with paired tasks MCP 5/7 and plain 0/7. The earlier .4 run had 19/21 fidelity and 19/21 tasks, with paired tasks MCP 7/7 and plain 0/7. These are separate historical runs. The two paired task failures were an omitted quantitative milk summary with inferred monitoring advice, and an incomplete adult label comparison. The three research failures were an omitted FAERS subset caveat, an absent numeric empty-year count and a disputed dose allegation plus an axis-placement concern. Fresh answers, live sources and model judgments can vary. Zero plain tasks fulfilled was not a finding that every answer was false. Current totals are in summary.json and REPORT.md.',
'## Completeness changes',
'The source retains available LactMed sections, adult and population sections from one label, explicit empty-year counts, the FAERS scope caveat, distinct maternal endpoints and numeric concentration passages. The final repair preserves report-only context beside empty outcome rows and requires neutral source-attributed wording. Both paired arms receive the same production clarification. The answer prompt changed; cases, criteria and grader v2 did not. Thirty-one test cases were added since .5, including five in .9. These are development-case repairs, not independent validation.',
'The intermediate .6 run retained research fidelity 20/21 and tasks 20/21, with paired tasks MCP 5/7 and plain 1/7. Its R01 concentration omission persisted; E01 task flags misattributed source doses to answers. The .7 payload-only pilot also omitted concentrations. The .8 R01 pilot included numeric concentrations, but its research run retained 20/21 fidelity and 18/21 tasks, exposing report-context and framing gaps. Full .8 pairs were intentionally not run. The final .9 pilot answers are reused once in their final sets. No completed answer was regenerated within the evaluated final configuration.',
'## Routing regression',
'The original “Give me a pregnancy evidence brief for lamotrigine” question completed with medication_evidence_brief as its first evidence call. Twelve direct deployed preflight checks cover positive variants, negation, incidental mention and overriding stops. They are separate from the 28-case benchmark and 42 final MLflow rows. The matcher remains a narrow English heuristic, not exhaustive language understanding.',
'No clinician adjudication occurred. Raw negative scores and all completed answers remain unchanged.']
(R/'TECHNICAL_REVIEW.md').write_text('\n\n'.join(parts)+'\n',encoding='utf-8')
print('Technical review preserves every negative grade and distinguishes manual observations.')
