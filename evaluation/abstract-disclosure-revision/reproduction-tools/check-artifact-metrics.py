"""Check published artifact figures against the retained evaluation summary."""
from pathlib import Path
from datetime import datetime, timezone
import json
import re
import zipfile
import xml.etree.ElementTree as ET

P = Path(r'C:/Users/piatkowskigs/Desktop/Parent-child Pharmacology MCP - Submission - 2026-11-20')
R = P / 'evaluation/abstract-disclosure-revision'
S = json.loads((R / 'summary.json').read_text(encoding='utf-8-sig'))
C, G, B = S['chat']['counts'], S['chat']['diagnostic_grading'], S['paired']
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def text(element, namespace):
    return ''.join(n.text or '' for n in element.findall('.//' + namespace + ':t', NS))

checks = []
def expect(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks.append(label)

deck = P / 'presentation/Parent-child Pharmacology MCP — Updated.pptx'
with zipfile.ZipFile(deck) as z:
    slides = {n: ET.fromstring(z.read(f'ppt/slides/slide{n}.xml')) for n in range(1, 50)}
    def shape(n, name):
        return next(text(s, 'a') for s in slides[n].findall('.//p:sp', NS)
                    if s.find('.//p:cNvPr', NS).get('name') == name)
    def cell(n, r, c):
        table = slides[n].find('.//a:tbl', NS)
        return text(table.findall('a:tr', NS)[r].findall('a:tc', NS)[c], 'a')
    expect('Slide 13 local tests', shape(13, 'metric-0'), str(S['local_tests']['tests']))
    expect('Slide 13 completion', shape(13, 'metric-1'), f"{C['completed']['passed']}/28")
    expect('Slide 13 stops', shape(13, 'metric-2'), f"{C['fixed_stops']['passed']}/7")
    for col, arm in [(1, 'mcp'), (2, 'plain')]:
        for slide in [14, 44]:
            expect(f'Slide {slide} {arm} completed', cell(slide, 1, col), f"{B[arm]['completed']}/7")
            expect(f'Slide {slide} {arm} tasks', cell(slide, 2, col), f"{B[arm]['task_fulfilled']}/7")
        expect(f'Slide 44 {arm} fidelity', cell(44, 3, col),
               f"{B[arm]['fidelity_pass']} / {B[arm]['fidelity_fail']} / {B[arm]['fidelity_not_assessable']}")
        expect(f'Slide 44 {arm} new answers', cell(44, 4, col), '7')
    expect('Slide 43 research grades', cell(43, 5, 1),
           f"{G['fidelity_pass']} fidelity pass, {G['fidelity_fail']} fail, {G['fidelity_not_assessable']} N/A; {G['task_fulfilled']}/21 tasks fulfilled")
    expect('Old deck test counts only on history slide',
           [n for n, root in slides.items() if re.search(r'\b(?:557|548|531|508)\b',text(root,'a'))], [47])

doc = P / 'documentation/Parent-child Pharmacology MCP - Evaluation.docx'
with zipfile.ZipFile(doc) as z:
    root = ET.fromstring(z.read('word/document.xml'))
    tables = root.findall('.//w:tbl', NS)
    table = next(t for t in tables if text(t.findall('w:tr', NS)[0].findall('w:tc', NS)[0], 'w') == 'Current measure')
    expected = ['592 passed', '30 passed', f"{C['completed']['passed']}/28", f"{C['boundary_behavior']['passed']}/28",
                f"{C['tool_selection']['passed']}/28", f"{C['fixed_stops']['passed']}/7",
                f"{C['citation_provenance']['passed']}/21", f"{G['fidelity_pass']} fidelity passes; {G['task_fulfilled']}/21 tasks"]
    for i, value in enumerate(expected, 1):
        expect(f'DOCX current metrics row {i}', text(table.findall('w:tr', NS)[i].findall('w:tc', NS)[1], 'w'), value)
    paragraphs = [text(p, 'w') for p in root.findall('w:body/w:p', NS)]
    expect('Old DOCX test counts only in history paragraph',
           [i for i, p in enumerate(paragraphs) if re.search(r'\b(?:557|548|531|508)\b',p)], [79])
    assert f"Tasks fulfilled: MCP {B['mcp']['task_fulfilled']}/7, plain {B['plain']['task_fulfilled']}/7" in paragraphs[69]
    checks.append('DOCX paired paragraph matches summary')

expect('Package index uses same complete summary', json.loads((P / 'evaluation/results.json').read_text(encoding='utf-8-sig'))['current_revision'], S)
expect('Package report points to final revision', json.loads((P / 'evaluation/results.json').read_text(encoding='utf-8-sig'))['current_report'], 'abstract-disclosure-revision/REPORT.md')
out = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'all_checks_passed': True,
       'checks': checks, 'count': len(checks), 'basis': 'Fresh-run summary.json; historical figures explicitly separated'}
(R / 'artifact-metric-consistency.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps({'metric_consistency_checks': len(checks), 'passed': True}))
