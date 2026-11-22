"""Offline language gate. Confidence is a heuristic score, not clinical validation."""
import re
from functools import lru_cache
ENGLISH_FUNCTION_WORDS = {'the','for','with','without','during','what','which','how','please','show','and','or','do','not','to','my','a','an','are','were','from'}
SELECTOR_WORDS = {'pregnancy','lactation','breastfeeding','breastfed','breast','milk','evidence','research','study','studies','maternal','fetal','foetal','neonatal','neonate','infant','child','adolescent','pediatric','paediatric','exposure','outcome','outcomes','pharmacokinetics','pharmacokinetic','registry','registries','clinical','trials','adverse','events'}

def contextual_english(text,score,whole):
    anchors=set(re.findall(r'[a-z]+',text.lower())) & ENGLISH_FUNCTION_WORDS
    return (whole['english'] and not score['foreign_confident'] and
            ((score['english_top'] and score['lingua_english']>=.35) or
             (score['lingua_english']>=.15 and len(anchors)>=2)))

def scientific_selector(text):
    """Short source selectors are data, not language-confidence evidence.

    The caller must preflight the actual question. Still reject confidently
    foreign phrases or detector failures when a multiword selector is supplied.
    """
    words=text.split()
    if not words or len(words)>6 or not all(re.fullmatch(r'[A-Za-z][A-Za-z0-9-]{1,79}',w) for w in words):return False
    if len(words)==1:return True
    # A name plus controlled English scientific concepts is a typed selector,
    # even when a detector mistakes international drug vocabulary for Latin/Dutch.
    lowered=[w.lower() for w in words]
    if any(w in SELECTOR_WORDS for w in lowered) and sum(w not in SELECTOR_WORDS for w in lowered)<=1:return True
    try:return not detector()(text)['foreign_confident']
    except Exception:return False

@lru_cache(maxsize=1)
def detector():
    from langdetect import detect_langs, DetectorFactory
    from lingua import LanguageDetectorBuilder, Language
    DetectorFactory.seed = 0
    lingua = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()
    def score(text):
        a = next((v.prob for v in detect_langs(text) if v.lang=='en'),0.0)
        values = lingua.compute_language_confidence_values(text)
        b = next((v.value for v in values if v.language == Language.ENGLISH), 0.0)
        return {'english': a >= .95 or b >= .80, 'english_top': bool(values and values[0].language == Language.ENGLISH),
                'lingua_english': b, 'foreign_confident': bool(values and values[0].language != Language.ENGLISH and values[0].value >= .80)}
    return score

def english_confidence(text):
    """Require English context; reject foreign clauses without treating weak fragments as languages."""
    try:
        parts = [p for p in re.split(r'[.!?;\n]+', text) if re.search(r'[^\W\d_]', p)]
        if not parts:
            return {'confident_english':False,'reason':'no_language_evidence'}
        words=text.split()
        if len(words)>8:
            parts += [' '.join(words[i:i+8]) for i in range(0,len(words)-7,4)]
        whole=detector()(text)
        scores=[detector()(p) for p in parts]
        # D05's "Do not provide medication decisions or doses" is ranked English
        # by Lingua but below the standalone threshold. Context may resolve an
        # ambiguous English-leading fragment, never a confidently foreign clause.
        passes=[s['english'] or contextual_english(p,s,whole) for p,s in zip(parts,scores)]
        return {'confident_english':whole['english'] and all(passes), 'segments_checked':len(passes),
                'method':'English whole-query threshold (langdetect >=.95 or Lingua >=.80), plus sentence/span checks. Ambiguous fragments need English context and either English ranked first (>=.35), or English >=.15 with two English function-word anchors. Confident foreign fragments do not inherit context.',
                'limitation':'Heuristic scores are not calibrated clinical confidence. Short technical phrases can be overblocked; mixed-language text can still be missed.'}
    except Exception:
        return {'confident_english':False,'reason':'language_detector_unavailable'}
