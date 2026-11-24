"""Apply the router fix to a policy.json (path in argv[1]). Idempotent: starts from git HEAD text."""
import json, sys, subprocess
path=sys.argv[1]
base=subprocess.run(['git','-C','/Users/gabrielapiatkowski/Parent-Child-Pharmacology-MCP','show','4298ad8:src/parent_child_pharmacology/core/policy.json'],capture_output=True).stdout.decode('utf-8')
crlf='\r\n' in base
p=json.loads(base); P=p['patterns']
KID=r"(?:infant|baby|child|toddler|kid|son|daughter|newborn|(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)[ -](?:year|month|week)s?[ -]old)"
# crisis: wider objects, intrusive thoughts, self-injury, not safe, pills to end it
P['crisis']=P['crisis'].replace(r"my\s+(?:baby|infant|child)|the\s+(?:baby|infant|child))", r"(?:my|the|our)\s+(?:baby|infant|child|newborn|son|daughter|kid|toddler))")
P['crisis']=P['crisis'].replace(r"(?:take|swallow)\s+(?:all|the\s+whole\s+bottle)", r"(?:tak\w+|swallow\w*)\s+(?:all|the\s+whole\s+bottle)")
P['crisis']=P['crisis'][:-3]+r"|(?:thoughts?|thinking|picturing|imagin\w+|fantasi\w+|urges?)\s+(?:of\s+|about\s+)?(?:myself\s+)?(?:hurt\w*|harm\w*|kill\w*|shak\w*|smother\w*|drown\w*|suffocat\w*|throw\w*|stab\w*)\s+(?:\w+\s+){0,2}(?:her|him|them|it|myself|(?:my|the|our)\s+(?:baby|infant|child|newborn|son|daughter|kid|toddler))|\b(?:i|myself)\b[^.?!]{0,40}\b(?:shak\w+|smother\w*|drown\w*|suffocat\w*|kill\w*)\s+(?:her|him|them|it)\b|disappear\w*\s+forever|(?:cut|cutting|burn\w*|injur\w+)\s+myself|keep\s+myself\s+safe|not\s+safe\s+(?:with|by)\s+myself|to\s+end\s+it\b|end(?:ing)?\s+my\s+life)\b"
# urgent: swelling, heavy bleeding, hard to wake, fainting, breathing, allergic reaction, infant high fever
P['urgent_event']+=r"|\b(?:face|tongue|lips?|throat)\b[^.?!]{0,25}\b(?:swell\w*|swollen|closing)\b|\b(?:swell\w*|swollen)\s+(?:face|tongue|lips?|throat)\b|\bbleeding\s+(?:heavily|a\s+lot|badly|and\s+(?:it\s+)?won't\s+stop)|(?:won't|will\s+not|wouldn't|isn't|not)\s+wak(?:e|ing)(?:\s+up)?\b|hard\s+to\s+(?:wake|rouse)|\b(?:fainted|passed\s+out|blacked\s+out)\b|breathing\s+(?:very\s+|really\s+|too\s+)?(?:slow\w*|shallow\w*)|barely\s+breathing|stopped\s+breathing|\bgasping\b|\b(?:having|have|has)\s+an?\s+(?:severe\s+|serious\s+|bad\s+)?allergic\s+reaction|\b(?:my|i|i'm|she|he)\b[^.?!]{0,60}\bhives\b|\b(?:is|are|keeps?)\s+(?:twitching|jerking)\b|\bfever\s+(?:of\s+)?10[3-9]\b|\b(?:i|she|he)\s+(?:have|has|am\s+having|is\s+having)\s+(?:severe\s+)?chest\s+pain"
# poison: more child words, more verbs and objects; too much given; bare 'overdose' needs a person or urgency
P['poison_exposure']=P['poison_exposure'].replace("|overdose)", r"|\b(?:i|my|he|she|we|they|baby|child|toddler|kid|son|daughter)\b[^.?!]{0,40}\boverdos\w*|\boverdos\w*\b[^.?!]{0,20}\b(?:now|just|help|emergency))")
P['poison_exposure']+=r"|\b"+KID+r"\b[^.?!]{0,40}\b(?:swallowed|ate|drank|ingested|chewed|got\s+into)\b[^.?!]{0,60}\b(?:pills?|tablets?|capsules?|medicine|medication|meds|supplements?|vitamins?|gumm\w+|melatonin|patch(?:es)?|bottle|pack|syrup|drops|cleaner|detergent|tylenol|motrin|advil|benadryl)\b|\b(?:took|gave|given|taken)\b[^.?!]{0,40}\btoo\s+(?:many|much)\b|\b(?:\d+|two|three|five|ten)\s+times\s+the\s+(?:amount|dose)\b"
# dose and treatment decisions
P['dose_or_treatment_decision']=P['dose_or_treatment_decision'].replace(r"(?:take|give|stop|start|continue|switch|change|increase|decrease)|how often", r"(?:take|give|stop|start|restart|resume|discontinue|continue|switch|change|increase|decrease)|how often")
P['dose_or_treatment_decision']=P['dose_or_treatment_decision'].replace(r"\b(?:dose|dosage|taper)|\b(?:give|tell", r"\b(?:dose|dosage|taper|schedule)|\b(?:give|tell")
P['dose_or_treatment_decision']=P['dose_or_treatment_decision'].replace(r"\b(?:sedat\w*|sleep through the night)\b.{0,60}\b(?:baby|infant)|\b(?:baby|infant)\b.{0,60}\b(?:sedat\w*|sleep through the night)", r"\b(?:sedate|sedating|sleep through the night)\b.{0,60}\b(?:baby|infant)|\b(?:baby|infant)\b.{0,60}\b(?:sedate\b|sedating|sleep through the night)")
P['dose_or_treatment_decision']+=r"|how\s+(?:much|many)\b[^?]{0,60}\b(?:should|can\s+(?:i|she|he|my)|is\s+safe|safe\s+for|to\s+(?:give|take))\b|\b(?:max(?:imum)?|highest|safe)\s+(?:amount|dose|dosage)\b|\bbetween\s+doses\b|\b(?:i|me|we|my\s+\w+)\b[^.?!]{0,30}\b(?:come|coming|go|going|get|getting|wean\w*)\s+off\b|\bdo\s+(?:i|we)\s+(?:need|have)\s+to\s+(?:stop|quit|start|switch|change|pump|wean|avoid|discontinue)\b|\btell\s+me\s+(?:whether|if)\s+(?:to|i\s+should)\b|\b(?:is\s+it|would\s+it\s+be)\s+(?:better|best|safer|time)\s+(?:for\s+(?:me|us|her|him)\s+)?to\s+(?:stop|start|quit|switch|continue|take|give|come|wean)\b|\bshould\s+(?:i|we)\s+(?:put|keep|take)\s+(?:my\s+\w+|her|him)\s+(?:on|off)\b|\b(?:which|what)\s+(?:is|would\s+be)\s+(?:the\s+)?(?:better|best|safer|safest)\b[^?]{0,30}\bfor\s+(?:me|us|my\s+\w+)\b"
P['decision_any_subject']=P['decision_any_subject'].replace(r"take|give|stop|start|continue|switch|change|increase|decrease|quit|wean)\b|\b(?:should|can|may|could)\s+(?:i|we", r"take|give|stop|start|restart|resume|discontinue|continue|switch|change|increase|decrease|quit|wean)\b|\b(?:should|can|may|could)\s+(?:i|we")
# vague identity: a class of medicine with no name
CLASS=r"(?:antibiotic|inhaler|heartburn|allergy|pain|nausea|fever|cough|cold|thyroid|diabetes|seizure|migraine|reflux|asthma)"
P['vague_identity']+=r"|\b(?:little|small|round|white|blue|pink|yellow|red|green|orange|purple)\s+(?:\w+\s+)?(?:pill|tablet|capsule|inhaler|liquid|syrup)\b|\b(?:my|that|this)\s+"+CLASS+r"(?:\s+(?:medicine|medication|med|pill|tablet))?\b(?!,?\s+(?:\(|called\s+|named\s+|is\s+))|\bthe\s+"+CLASS+r"\s+(?:medicine|medication|pills?)\s+in\s+my\b|\bthe\s+(?:stuff|one|new\s+one|medicine|medication|pill|thing)\s+(?:that\s+)?(?:the\s+pharmacist|my\s+(?:doctor|ob|midwife|pediatrician)|i|she|he)\s+(?:gave|prescribed|started|take|takes|use|uses)\b"
# identifiers written without a colon
P['personal_identifiers']+=r"|\b(?:mrn|medical\s+record\s+number|member\s+id|insurance\s+(?:id|number)|policy\s+number)\b\s*(?:is|#|:|=)?\s*[a-z]*\d{4,}|\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b|\b(?:dob|date\s+of\s+birth|born|birthday)\b[^.?!]{0,25}\b\d{1,2}/\d{1,2}/\d{2,4}\b"
# fiction and role-play framings
P['instruction_override']+=r"|\bfor\s+(?:a|my)\s+(?:novel|story|screenplay|script|book|play|game)\b|\bhypothetically\b|\brole-?play\b|\bif\s+you\s+were\s+my\s+(?:doctor|physician|pharmacist|pediatrician|ob|midwife)\b|\byou\s+are\s+my\s+(?:doctor|physician|pediatrician|pharmacist|ob|midwife)\b"
# off-topic
P['off_topic_task']+=r"|\b(?:python|javascript|code|coding|spreadsheet|world\s+series|super\s+bowl|stocks?|invest\w*|crypto\w*|birthday|party|vacation|election|lyrics)\b|\btranslate\s+(?:this|the|that)\b"
p['version']='2026-11-23.30'
text=json.dumps(p,indent=2,ensure_ascii=False)+'\n'
if crlf: text=text.replace('\n','\r\n')
open(path,'w',newline='',encoding='utf-8').write(text)
print('patched',path)
