"""FDA's public pediatric labeling-change workbook (not an openFDA endpoint)."""
import asyncio
from datetime import date, datetime, timezone
import hashlib
from io import BytesIO
import re
from openpyxl import load_workbook
from core.http import http

PAGE_URL = 'https://www.fda.gov/science-research/pediatrics/pediatric-labeling-changes'
DATA_URL = 'https://www.fda.gov/media/175738/download?attachment'
COLUMNS = {
 'FDA Application Number(s)': 'application_numbers',
 'Pediatric Labeling Approval Date': 'labeling_change_date',
 'Trade Name': 'trade_name', 'Generic Name': 'generic_name',
 'Type of Legislation': 'legislation', 'Indication': 'indication',
 'Indication(s) Studied': 'indications_studied',
 'Labeling Change Summary': 'labeling_change_summary',
 'Therapeutic Category': 'therapeutic_category', 'Dosage Form(s)': 'dosage_forms',
 'Route(s) of Administration': 'routes', 'Studied in Neonates': 'studied_in_neonates',
 'Indicated in Neonates': 'indicated_in_neonates',
}
REQUIRED = {'Pediatric Labeling Approval Date', 'Trade Name', 'Generic Name',
            'Type of Legislation', 'Labeling Change Summary'}


def parse_workbook(content: bytes) -> list[dict]:
    """Preserve FDA row-level scope; missing values stay null, not negative findings."""
    wb = load_workbook(BytesIO(content), read_only=True, data_only=True)
    try:
        ws = wb.worksheets[0]
        rows = ws.iter_rows(values_only=True)
        headers = [str(v).strip() if v is not None else '' for v in next(rows)]
        if not REQUIRED.issubset(headers):
            raise ValueError('FDA pediatric workbook schema changed')
        result = []
        for row_number, values in enumerate(rows, 2):
            raw = dict(zip(headers, values))
            if not raw.get('Trade Name') and not raw.get('Generic Name'):
                continue
            record = {key: (str(raw.get(header)).strip() if raw.get(header) is not None else None)
                      for header, key in COLUMNS.items()}
            value = raw.get('Pediatric Labeling Approval Date')
            if isinstance(value, (date, datetime)):
                record['labeling_change_date'] = value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
            else:
                raise ValueError('FDA pediatric workbook date format changed')
            record.update(source_sheet=ws.title, source_row=row_number, url=PAGE_URL, dataset_url=DATA_URL)
            result.append(record)
        if not result:
            raise ValueError('FDA pediatric workbook contains no records')
        return result
    finally:
        wb.close()


def select_records(rows: list[dict], drug: str, legislation: str, limit: int) -> tuple[list[dict], int]:
    tokens = re.findall(r'[^\W_]+', drug.casefold(), re.UNICODE)
    if not tokens:
        raise ValueError('Provide a medication name')
    if legislation not in {'any', 'BPCA', 'PREA'}:
        raise ValueError('Invalid legislation filter')
    def matches(row):
        words = set(re.findall(r'[^\W_]+', ((row.get('trade_name') or '')+' '+(row.get('generic_name') or '')).casefold()))
        return (all(t in words for t in tokens) and
                (legislation == 'any' or legislation in (row.get('legislation') or '').upper()))
    matches_list = sorted((r for r in rows if matches(r)), key=lambda r: r['labeling_change_date'], reverse=True)
    return matches_list[:max(1, min(limit, 20))], len(matches_list)


async def search(drug: str, legislation: str = 'any', max_results: int = 10) -> dict:
    if not drug.strip() or len(drug) > 200 or not re.search(r'\w', drug):
        return {'source': 'validation', 'error': 'invalid_drug', 'url': PAGE_URL}
    response = await http.request('GET', DATA_URL, ttl=3600)
    rows = await asyncio.to_thread(parse_workbook, response.content)
    results, count = select_records(rows, drug, legislation, max_results)
    return {'source': 'live:fda:pediatric-labeling-workbook', 'url': PAGE_URL, 'dataset_url': DATA_URL,
            'queried_at_utc': datetime.now(timezone.utc).isoformat(),
            'dataset_sha256': hashlib.sha256(response.content).hexdigest(),
            'dataset_row_count': len(rows), 'dataset_latest_change_date': max(r['labeling_change_date'] for r in rows),
            'cache_note': 'FDA workbook response may be cached for up to one hour; query time is not publication time.',
            'matching_records': count, 'returned_records': len(results), 'results_truncated': count > len(results),
            'results': results, 'legislation_filter': legislation,
            'search_scope': 'All name tokens must match trade/generic name fields; no automatic synonym expansion. Try the generic ingredient or brand separately.',
            'caveats': ['Historical labeling changes, not the complete current label or a treatment recommendation.',
                        'BPCA and PREA are legislative categories; BPCA designation does not establish NIH funding.',
                        'A change can report negative findings or limitations, not necessarily a new pediatric approval.',
                        'Age ranges, indications and formulations must be read from the returned source text. Missing fields are unknown.',
                        'No match is not evidence of no pediatric research, no approval, or safety.']}
