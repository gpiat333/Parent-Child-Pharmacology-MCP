"""Pure parser for published aggregate MPRINT Gold outcomes."""
import csv
import io
import re


def normalize_pmid(value):
    text=str(value or '').strip()
    if not re.fullmatch(r'[1-9][0-9]{0,9}(?:\.0+)?',text):
        return None
    return text.split('.')[0]


def parse_outcomes(content, kind):
    if kind not in {'PE_CT','PK_summary'}:
        raise ValueError('Unsupported outcome table')
    reader=csv.DictReader(io.StringIO(content.decode('utf-8-sig')))
    required={'PMID','Value','Unit','_source_file','_source_folder','_row_index'}
    required.add('Outcomes' if kind=='PE_CT' else 'Outcome')
    if not required.issubset(reader.fieldnames or []):
        raise ValueError('MPRINT outcome schema changed')
    for row_number,row in enumerate(reader,2):
        pmid=normalize_pmid(row.get('PMID'))
        yield {'pmid':pmid,'source_row':row_number,
               'curation_workbook':row['_source_file'].strip(),
               'curation_folder':row['_source_folder'].strip(),
               'source_fields':{k:(v.strip() or None) for k,v in row.items() if k and v is not None}}
