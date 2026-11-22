"""Versioned public-source filters; IC codes map to RePORTER agency names."""
from typing import Literal
IC = Literal['any','AA','AG','AI','AR','AT','CA','CC','DA','DC','DE','DK','EB','ES','EY','GM','HD','HG','HL','LM','MD','MH','NR','NS','OD','RR','TR','TW']
IC_AGENCIES={'AA':'NIAAA','AG':'NIA','AI':'NIAID','AR':'NIAMS','AT':'NCCIH','CA':'NCI','CC':'CC',
 'DA':'NIDA','DC':'NIDCD','DE':'NIDCR','DK':'NIDDK','EB':'NIBIB','ES':'NIEHS','EY':'NEI','GM':'NIGMS',
 'HD':'NICHD','HG':'NHGRI','HL':'NHLBI','LM':'NLM','MD':'NIMHD','MH':'NIMH','NR':'NINR','NS':'NINDS',
 'OD':'OD','RR':'NCRR','TR':'NCATS','TW':'FIC'}
PublicationType=Literal['any','randomized_controlled_trial','systematic_review','meta_analysis','observational_study','case_report']
PUBLICATION_TYPES={'randomized_controlled_trial':'Randomized Controlled Trial','systematic_review':'Systematic Review',
 'meta_analysis':'Meta-Analysis','observational_study':'Observational Study','case_report':'Case Reports'}

def literature_filters(params,publication_type='any',date_from=None,date_to=None):
    from datetime import date
    if publication_type!='any':params['term']+=' AND "'+PUBLICATION_TYPES[publication_type]+'"[Publication Type]'
    if date_from or date_to:
        for v in [date_from,date_to]:
            if v:date.fromisoformat(v)
        if date_from and date_to and date_from>date_to:raise ValueError('date_from must not follow date_to')
        params.pop('reldate',None)
        params.update(datetype='pdat',mindate=(date_from or '1800-01-01').replace('-','/'),maxdate=(date_to or '3000-12-31').replace('-','/'))
    return params
