"""PLLR 8.1 extraction, retaining empty subsections and source-only dosing context."""
import re
import xml.etree.ElementTree as ET

HEADINGS = {'risk summary':'risk_summary', 'clinical considerations':'clinical_considerations', 'data':'data',
            'pregnancy exposure registry':'pregnancy_exposure_registry'}
CLINICAL = {
    'Disease-associated maternal and/or embryo/fetal risk':'disease_associated_risk',
    'Dose adjustments during pregnancy and the postpartum period':'dose_adjustments',
    'Maternal adverse reactions':'maternal_adverse_reactions',
    'Fetal/Neonatal adverse reactions':'fetal_neonatal_adverse_reactions',
    'Labor or delivery':'labor_or_delivery',
}

def text_blocks(element):
    """Keep SPL paragraph/heading boundaries; itertext alone loses headings."""
    if element is None: return ''
    chunks=[]
    def walk(node):
        if node.tag.rsplit('}',1)[-1] in {'paragraph','title','br','item','tr'}: chunks.append('\n')
        if node.text: chunks.append(node.text)
        for child in node:
            walk(child)
            if child.tail: chunks.append(child.tail)
        if node.tag.rsplit('}',1)[-1] in {'paragraph','title','item','tr'}: chunks.append('\n')
    walk(element)
    return '\n'.join(re.sub(r'\s+',' ',x).strip() for x in ''.join(chunks).splitlines() if x.strip())

def split_headings(text, headings):
    # Heading matching is anchored to a block boundary, never a prose mention
    # such as "see Data". Inline bold SPL headings begin a paragraph as well.
    pattern=re.compile(r'(?im)^\s*(?:8\.1\s*)?('+'|'.join(re.escape(h) for h in sorted(headings,key=len,reverse=True))+r')\s*(?:[:\-]\s*|\n|$)')
    matches=list(pattern.finditer(text));out={v:None for v in headings.values()}
    for i,m in enumerate(matches):
        value=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)].strip()
        key=next(v for k,v in headings.items() if k.casefold()==m[1].casefold())
        if value: out[key]=value
    return out

def parse_pllr(xml=None, pregnancy_text=None, max_chars=16000):
    raw=pregnancy_text or ''
    if xml:
        ns={'h':'urn:hl7-org:v3'}
        for sec in ET.fromstring(xml).iterfind('.//h:section',ns):
            title=re.sub(r'^[\d.\s]+','',text_blocks(sec.find('h:title',ns))).strip().lower()
            code=sec.find('h:code',ns)
            if title=='pregnancy' or (not title and code is not None and code.get('code')=='42228-7'):
                raw=text_blocks(sec.find('h:text',ns))
                # Some SPLs encode subheadings as child sections.
                for component in sec.findall('h:component',ns): raw+='\n'+text_blocks(component)
                break
    subsections=split_headings(raw,HEADINGS)
    clinical=split_headings(subsections['clinical_considerations'] or '',CLINICAL)
    data_topics=split_headings(subsections['data'] or '',{'Human Data':'human','Animal Data':'animal'})
    fields={key:{'text':value[:max_chars] if value else None,'found':bool(value),'truncated':bool(value and len(value)>max_chars)} for key,value in subsections.items()}
    return {'section':'8.1 Pregnancy','subsections':fields,'clinical_consideration_topics':clinical,'data_topics':data_topics,
            'parse_status':'pllr_headings_found' if any(subsections.values()) else 'headings_not_found',
            'maternal_dose_adjustment':{'clinical_considerations_text':fields['clinical_considerations']['text'],
                'dose_adjustment_text':clinical['dose_adjustments'], 'dose_adjustment_data_found':bool(clinical['dose_adjustments']),
                'source_context_only':True,'personal_dosing_instruction':False,
                'message':'Source labeling for clinician discussion, never an individualized dose. Clinical Considerations may concern risks without containing dose-adjustment data.'},
            'limitations':['An absent/unparsed subsection is not proof that no data exist. Older or combined OTC labels may not follow PLLR.',
                           'Clinical Considerations is not synonymous with maternal pharmacokinetic evidence.']}
