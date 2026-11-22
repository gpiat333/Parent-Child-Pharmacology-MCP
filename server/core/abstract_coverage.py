"""PubMed retrieval coverage; a missing abstract is not a finding about a study."""
import json
import re

FIELDS = ('with_abstract_pmids', 'without_abstract_pmids', 'unreturned_pmids', 'failed_pmids')
TOOLS = {'get_abstracts', 'medication_evidence_brief'}


def coverage(pmids, articles, request_failed=False, search_failed=False):
    requested = list(dict.fromkeys(pmids))
    groups = {key: [] for key in FIELDS}
    for pmid in requested:
        rows = [a for a in articles if a.get('pmid') == pmid]
        if request_failed:
            key = 'failed_pmids'
        elif any(isinstance(a.get('abstract'), str) and a['abstract'].strip() for a in rows):
            key = 'with_abstract_pmids'
        elif rows:
            key = 'without_abstract_pmids'
        else:
            key = 'unreturned_pmids'
        groups[key].append(pmid)
    return merge_coverages([{'schema_version': 1, 'requested_pmids': requested,
                            'search_failed': bool(search_failed), **groups}])


def merge_coverages(blocks):
    """Latest retrieval state wins per PMID, including a later successful refetch."""
    states = {}
    search_failed = False
    for block in blocks:
        if block.get('schema_version') != 1:
            raise ValueError('Unsupported abstract coverage schema')
        requested = block.get('requested_pmids')
        if not isinstance(requested, list) or any(not isinstance(x, str) or not re.fullmatch(r'[1-9][0-9]{0,9}', x) for x in requested):
            raise ValueError('Invalid abstract coverage PMIDs')
        flattened = []
        for key in FIELDS:
            values = block.get(key)
            if not isinstance(values, list) or any(x not in requested for x in values):
                raise ValueError('Invalid abstract coverage group')
            flattened.extend(values)
            for pmid in values:
                states[pmid] = key
        if len(flattened) != len(set(flattened)) or set(flattened) != set(requested):
            raise ValueError('Abstract coverage groups must partition requested PMIDs')
        search_failed = search_failed or block.get('search_failed') is True
    groups = {key: [pmid for pmid, state in states.items() if state == key] for key in FIELDS}
    incomplete = search_failed or any(groups[key] for key in FIELDS[1:])
    return {'schema_version': 1, 'requested_pmids': list(states), **groups,
            'search_failed': search_failed, 'requested_count': len(states),
            'abstract_text_count': len(groups['with_abstract_pmids']),
            'incomplete': bool(incomplete), 'disclosure_required': bool(incomplete or not states),
            'scope': 'Requested PubMed records only; not a complete literature review.'}


def unpack_result(value):
    if not isinstance(value, dict):
        return {}
    if isinstance(value.get('structuredContent'), dict):
        return value['structuredContent']
    if isinstance(value.get('content'), list):
        for item in value['content']:
            if item.get('type') == 'text':
                try:
                    parsed = json.loads(item.get('text', ''))
                except (TypeError, ValueError):
                    continue
                if isinstance(parsed, dict):
                    return parsed
    return value


def disclosure_notices(tool_calls, templates):
    blocks = []
    for call in tool_calls or ():
        if call.get('tool') not in TOOLS:
            continue
        result = unpack_result(call.get('result'))
        if result.get('allow_research') is False or result.get('requires_confirmation'):
            continue
        if isinstance(result.get('abstract_coverage'), dict) and result['abstract_coverage']:
            blocks.append(result['abstract_coverage'])
    if not blocks:
        return []
    merged = merge_coverages(blocks)
    if not merged['disclosure_required']:
        return []
    parts = []
    if merged['requested_count']:
        parts.append(templates['counts'].format(found=merged['abstract_text_count'], requested=merged['requested_count']))
        for key in FIELDS[1:]:
            if merged[key]:
                parts.append(templates[key].format(ids=', '.join(merged[key])))
    elif not merged['search_failed']:
        parts.append(templates['no_records'])
    if merged['search_failed']:
        parts.append(templates['search_failed'])
    parts.append(templates['limit'])
    return [{'id': 'pubmed_abstract_coverage', 'text': ' '.join(parts),
             'origin': 'Application retrieval-coverage contract; not a source finding',
             'display_required': True}]
