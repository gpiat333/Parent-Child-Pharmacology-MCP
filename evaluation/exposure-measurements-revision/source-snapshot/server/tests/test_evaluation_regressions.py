import asyncio
import httpx
from mc import sources as src


def test_mismatched_spl_titles_are_not_misclassified():
    xml = '''<document xmlns="urn:hl7-org:v3"><section>
    <code code="42229-5"/><title>8.1. Pregnancy</title><text>Pregnancy evidence.</text>
    </section><section><code code="34080-2"/><title>8.4. Pediatric Use</title>
    <text>Children studied.</text></section><section><code code="34081-0"/>
    <title>8.5. Geriatric Use</title><text>Older adults studied.</text></section></document>'''
    result = src.parse_dailymed_sections(xml)
    assert 'Children studied.' in result['pediatric_use']
    assert 'Older adults' not in result['pediatric_use']
    assert 'Pregnancy evidence.' in result['pregnancy']
    assert len(src.dailymed_section_warnings(xml)) == 3


def test_explicit_other_section_does_not_inherit_pediatric_code():
    xml = '<document xmlns="urn:hl7-org:v3"><section><code code="34081-0"/><title>Geriatric Use</title><text>Age 65.</text></section></document>'
    assert src.parse_dailymed_sections(xml) == {}


def test_invalid_lactmed_id_makes_no_network_call(monkeypatch):
    async def forbidden(*args, **kwargs):
        raise AssertionError('Invalid ID must not reach NCBI')
    monkeypatch.setattr(src, '_ncbi', forbidden)
    result = asyncio.run(src.lactmed_record('diphenhydramine'))
    assert 'search_lactmed' in result['error']


def rxnorm_mock(monkeypatch, exact, properties):
    async def request(method, url, **kwargs):
        if url.endswith('/rxcui.json'):
            body = {'idGroup': {'rxnormId': ['36437'] if exact else []}}
        elif url.endswith('/approximateTerm.json'):
            body = {'approximateGroup': {'candidate': [{'rxcui': '36437'}]}}
        elif url.endswith('/properties.json'):
            body = {'properties': properties}
        else:
            raise AssertionError(url)
        return httpx.Response(200, json=body)
    monkeypatch.setattr(src.http, 'request', request)


def test_unknown_rxnorm_candidate_is_not_found(monkeypatch):
    rxnorm_mock(monkeypatch, False, {})
    result = asyncio.run(src.rxnorm_normalize('zorbaxilin-xyz'))
    assert result['found'] is False
    assert 'rxcui' not in result


def test_approximate_rxnorm_identity_requires_confirmation(monkeypatch):
    rxnorm_mock(monkeypatch, False, {'name': 'sertraline', 'tty': 'IN'})
    result = asyncio.run(src.rxnorm_normalize('sertaline'))
    assert result['requires_confirmation'] is True
    assert result['match_type'] == 'approximate'


def test_exact_rxnorm_identity_is_confirmed(monkeypatch):
    rxnorm_mock(monkeypatch, True, {'name': 'sertraline', 'tty': 'IN'})
    result = asyncio.run(src.rxnorm_normalize('sertraline'))
    assert result['found'] and not result['requires_confirmation']


def test_faers_query_has_reproducible_cohort_and_limit():
    params = src.faers_query_params('ondansetron', 'pregnancy', 8)
    assert 'foetal exposure during pregnancy' in params['search']
    assert 'ondansetron' in params['search']
    assert params['limit'] == 8


def test_brief_does_not_research_unconfirmed_candidate(monkeypatch):
    import server
    async def uncertain(name):
        return {'found': True, 'requires_confirmation': True, 'ingredients': ['sertraline']}
    async def forbidden(*args, **kwargs):
        raise AssertionError('Unconfirmed drug must not be researched')
    monkeypatch.setattr(src, 'rxnorm_normalize', uncertain)
    monkeypatch.setattr(src, 'pubmed_search', forbidden)
    monkeypatch.setattr(src, 'dailymed_label', forbidden)
    result = asyncio.run(server.medication_evidence_brief.__wrapped__('sertaline'))
    assert result['requires_confirmation']
    assert 'queried_as' not in result
