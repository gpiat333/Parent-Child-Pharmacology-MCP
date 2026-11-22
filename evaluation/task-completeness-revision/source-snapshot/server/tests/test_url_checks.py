"""Citation boundary regression using the actual previously failed answer."""
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[2]
spec=importlib.util.spec_from_file_location('url_checks',ROOT/'chat-client/url_checks.py')
uc=importlib.util.module_from_spec(spec);spec.loader.exec_module(uc)


@pytest.mark.parametrize('text,expected',[
    ('[S1](https://a.gov/x)[S2](https://b.gov/y/)', ['https://a.gov/x','https://b.gov/y/']),
    ('[one](https://a.gov/x) [two](https://b.gov/y)', ['https://a.gov/x','https://b.gov/y']),
    ('[Study](https://a.gov/a_(b))',['https://a.gov/a_(b)']),
    ('[Study](https://a.gov/a_(b(c)))',['https://a.gov/a_(b(c))']),
    (r'[Study](https://a.gov/a_\(b\))',['https://a.gov/a_(b)']),
    ('[Study](https://a.gov/x "Source title")',['https://a.gov/x']),
    ('<https://a.gov/x?q=one&amp;n=2>',['https://a.gov/x?q=one&n=2']),
    ('See https://a.gov/x. Then https://b.gov/y,',['https://a.gov/x','https://b.gov/y']),
    ('(https://a.gov/a_(b)).',['https://a.gov/a_(b)']),
    ('`https://a.gov/x`',['https://a.gov/x']),
    ('[ref]: https://a.gov/x',['https://a.gov/x']),
    ('No citations here.',[]),
    ('[Broken](https://) and ftp://example.gov',[]),
])
def test_url_boundaries(text,expected):
    assert uc.extract_urls(text)==expected


def test_unretrieved_url_and_changed_query_still_fail_membership():
    result=uc.check_url_membership('[a](https://a.gov/x?q=2)[b](https://b.gov/x)',['https://a.gov/x?q=1'])
    assert not result['citation_provenance']
    assert result['unmatched_urls']==['https://a.gov/x?q=2','https://b.gov/x']


def test_missing_citation_still_fails():
    assert not uc.check_url_membership('No links.',['https://a.gov/x'])['citation_provenance']


def test_previous_r12_adjacent_links_match_the_actual_saved_tool_outputs():
    raw=json.loads((ROOT/'evaluation/brief-routing-revision/chats/R12-results.json').read_text(encoding='utf-8-sig'))
    def strings(v):
        if isinstance(v,str):
            try:yield from strings(json.loads(v))
            except (ValueError,TypeError):yield v
        elif isinstance(v,dict):
            for x in v.values():yield from strings(x)
        elif isinstance(v,list):
            for x in v:yield from strings(x)
    result=uc.check_url_membership(raw['answer'],list(strings(raw['tool_calls'])))
    assert result['citation_provenance'] and not result['unmatched_urls']
    assert len(set(result['answer_urls']))==2
