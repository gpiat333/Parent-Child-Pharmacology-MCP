"""Offline language gate. Confidence is a heuristic score, not clinical validation."""

import re
from functools import lru_cache

ENGLISH_FUNCTION_WORDS = {
    "the",
    "for",
    "with",
    "without",
    "during",
    "what",
    "which",
    "how",
    "please",
    "show",
    "and",
    "or",
    "do",
    "not",
    "to",
    "my",
    "a",
    "an",
    "are",
    "were",
    "from",
}
SELECTOR_WORDS = {
    "pregnancy",
    "lactation",
    "breastfeeding",
    "breastfed",
    "breast",
    "milk",
    "evidence",
    "research",
    "study",
    "studies",
    "maternal",
    "fetal",
    "foetal",
    "neonatal",
    "neonate",
    "infant",
    "child",
    "adolescent",
    "pediatric",
    "paediatric",
    "exposure",
    "outcome",
    "outcomes",
    "pharmacokinetics",
    "pharmacokinetic",
    "registry",
    "registries",
    "clinical",
    "trials",
    "adverse",
    "events",
}
SELECTOR_WORDS.update(
    {"serum", "cord", "blood", "placental", "placenta", "concentration", "concentrations"}
)

# International mathematical terms can look like Latin to language detectors.
# Admit only complete, bounded English task clauses in an English question;
# this is not an exemption for arbitrary text labeled "research" or "audit".
TASK_GRAMMAR = set(
    "for each which has have the a an and or of from to with without all both every only not in as by its their that these those".split()
)
TASK_VOCABULARY = set(
    "check compare compute calculate return select find inspect count review add subtract multiply divide sum difference maximum minimum mean median range spread numeric number numbers value values label labels gold silver exposure exposures outcome outcomes row rows record records zero one two three four five six seven eight nine ten largest smallest greater greatest less least exact integer decimal places".split()
)
TASK_ACTIONS = set(
    "check compare compute calculate return select find inspect count review add subtract multiply divide maximum minimum".split()
)
TASK_VOCABULARY.update({"plus", "minus"})
TASK_VOCABULARY.update({"public", "study", "studies", "dataset", "data"})


def technical_english_clause(text, whole):
    words = re.findall(r"[a-z]+", text.lower())
    tokens = set(words)
    return bool(
        whole["english"]
        and 3 <= len(words) <= 16
        and len(tokens & TASK_GRAMMAR) >= 2
        and tokens & TASK_ACTIONS
        and tokens <= TASK_GRAMMAR | TASK_VOCABULARY
    )


def mask_longest_term(text):
    """Replace the single longest word (usually a medicine or condition name).

    Detectors read many INN drug names and clinical terms as Latin/Italian.
    Only one token is masked, and the result must still pass the stricter
    contextual check, so a clause written in another language stays blocked.
    """
    words = re.findall(r"[A-Za-z][A-Za-z'-]{6,}", text)
    if not words:
        return None
    return text.replace(max(words, key=len), "it", 1)


def contextual_english(text, score, whole):
    anchors = set(re.findall(r"[a-z]+", text.lower())) & ENGLISH_FUNCTION_WORDS
    return (
        whole["english"]
        and not score["foreign_confident"]
        and (
            (score["english_top"] and score["lingua_english"] >= 0.35)
            or (score["lingua_english"] >= 0.15 and len(anchors) >= 2)
        )
    )


def scientific_selector(text):
    """Short source selectors are data, not language-confidence evidence.

    The caller must preflight the actual question. Still reject confidently
    foreign phrases or detector failures when a multiword selector is supplied.
    """
    words = text.split()
    if (
        not words
        or len(words) > 6
        # Names such as "5-ASA" or "St. John's wort" carry digits and punctuation.
        or not all(
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9'.-]{1,79}", w) and re.search(r"[A-Za-z]{2}", w)
            for w in words
        )
    ):
        return False
    if len(words) == 1:
        return True
    # A name plus controlled English scientific concepts is a typed selector,
    # even when a detector mistakes international drug vocabulary for Latin/Dutch.
    lowered = [w.lower() for w in words]
    if (
        any(w in SELECTOR_WORDS for w in lowered)
        and sum(w not in SELECTOR_WORDS for w in lowered) <= 1
    ):
        return True
    try:
        return not detector()(text)["foreign_confident"]
    except Exception:
        return False


QUESTION_STARTS = set(
    "do does did is are was were can could may might should will would what which who when where why how has have tell show find give list compare summarize explain".split()
)
COMMON_ENGLISH = set(
    """a an the and or but if of to in on at for with without from by about into during while after before since than
    as is are was were be been being am do does did done have has had can could may might must shall should will would
    not no yes it its this that these those there here what which who whom whose when where why how i me my mine we
    us our you your he him his she her they them their baby babies child children kid kids son daughter infant infants
    newborn newborns toddler toddlers mom moms mother mothers women woman pregnant pregnancy breastfeeding breastfeed
    nursing pumping postpartum milk supply safe safety okay ok fine risk risks harm harmful cause causes caused effect effects side use
    using used take taking took give giving stop start continue get getting help any some all more most less much
    many other same different really still also just only very too well good bad known know say says said research
    evidence study studies data oil oils essential vitamin vitamins supplement supplements herb herbs herbal tea drug
    drugs medicine medicines medication medications pill pills vaccine vaccines shot shots link linked
    links source sources fda nih cdc nlm nichd lactmed pubmed mprint dailymed medlineplus label labels warning
    warnings recall recalls record records abstract abstracts article articles paper papers trial registry
    brief short long simple plain language please thanks again now then""".split()
)
# Commands and conversational openers that begin ordinary English requests ("Link the studies.").
DIRECTIVE_STARTS = set(
    "link include cite search get check describe separate provide keep use add also and then now please "
    "thanks thank ok okay great so but look focus limit sort repeat continue".split()
)
FOREIGN_FUNCTION_WORDS = set(
    "el la los las del en y que para por con durante puedo tomar mi es seguro embarazo lactancia bebé le les du des "
    "pendant je est et pour avec une der das und ich ist nicht mit für os com não posso gravidez il di gravidanza "
    "mientras puis".split()
)


STATEMENT_STARTS = set(
    "i i'm im i've i'd my we we're our she she's he he's they they're their her his it it's this the "
    "baby child son daughter".split()
)


def english_question_frame(text):
    """Short plain English questions the detectors under-score ("Do vaccines cause autism?",
    "I'm breastfeeding. Can I take ibuprofen?").

    Each sentence must open with an English question word or a common English statement opener,
    use mostly common English words with at most two other words (usually a medicine or condition
    name), contain no common Spanish, French, German, Portuguese or Italian function words, and at
    least one sentence must be a question. The whole text must not be confidently foreign.
    """
    sentences = [re.findall(r"[a-zà-ÿ']+", part.lower()) for part in re.split(r"[.!?;\n]+", text)]
    sentences = [w for w in sentences if w]
    total = sum(len(w) for w in sentences)
    if not sentences or not 2 <= total <= 40 or len(sentences) > 4:
        return False
    known = (
        COMMON_ENGLISH
        | ENGLISH_FUNCTION_WORDS
        | SELECTOR_WORDS
        | QUESTION_STARTS
        | DIRECTIVE_STARTS
        | STATEMENT_STARTS
    )
    asked = False
    masked = []
    for words in sentences:
        if words[0] in QUESTION_STARTS or words[0] in DIRECTIVE_STARTS:
            asked = True
        elif words[0] not in STATEMENT_STARTS:
            return False
        if any(w in FOREIGN_FUNCTION_WORDS for w in words):
            return False
        unknown = [w for w in words if w not in known]
        if len(unknown) > 2 or len(unknown) * 2 > len(words):
            return False
        # Medicine names fool detectors; check the sentence with them replaced by "it".
        masked.append(" ".join("it" if w not in known else w for w in words))
    if not asked:
        return False
    try:
        return not detector()(". ".join(masked) + "?")["foreign_confident"]
    except Exception:
        return False


TOPIC_WORDS = {"neonates", "infants", "children", "levels", "safety", "nursing", "drugs"}


def short_topic_phrase(text):
    """A medicine name, or a name with English topic words, typed instead of a full question
    ("sertraline", "lamotrigine breastfeeding levels").

    Detectors cannot score these: a drug name alone has no language. A single name is accepted
    as a lookup key. A longer phrase needs at least one common English word and at most two
    other words, and no Spanish, French, German, Portuguese or Italian function word, so
    "sertralina lactancia" and "Ibuprofen Stillzeit" still stop.
    """
    words = re.findall(r"[a-zà-ÿ0-9'-]+", text.lower())
    if not words or len(words) > 6 or re.search(r"[?¿¡]", text) or not scientific_selector(text):
        return False
    if any(w in FOREIGN_FUNCTION_WORDS for w in words):
        return False
    if len(words) == 1:
        return True
    known = COMMON_ENGLISH | ENGLISH_FUNCTION_WORDS | SELECTOR_WORDS | TOPIC_WORDS
    unknown = [w for w in words if w not in known]
    return len(unknown) < len(words) and len(unknown) <= 2


@lru_cache(maxsize=1)
def detector():
    from langdetect import DetectorFactory, detect_langs
    from lingua import Language, LanguageDetectorBuilder

    DetectorFactory.seed = 0
    lingua = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()

    def score(text):
        a = next((v.prob for v in detect_langs(text) if v.lang == "en"), 0.0)
        values = lingua.compute_language_confidence_values(text)
        b = next((v.value for v in values if v.language == Language.ENGLISH), 0.0)
        return {
            "english": a >= 0.95 or b >= 0.80,
            "english_top": bool(values and values[0].language == Language.ENGLISH),
            "lingua_english": b,
            "foreign_confident": bool(
                values and values[0].language != Language.ENGLISH and values[0].value >= 0.80
            ),
        }

    return score


def english_confidence(text):
    """Require English context; reject foreign clauses without treating weak fragments as languages."""
    try:
        parts = [p for p in re.split(r"[.!?;\n]+", text) if re.search(r"[^\W\d_]", p)]
        if not parts:
            return {"confident_english": False, "reason": "no_language_evidence"}
        words = text.split()
        if len(words) > 8:
            parts += [" ".join(words[i : i + 8]) for i in range(0, len(words) - 7, 4)]
        whole = detector()(text)
        whole["english"] = whole["english"] or technical_english_clause(text, {"english": True})
        scores = [detector()(p) for p in parts]

        # D05's "Do not provide medication decisions or doses" is ranked English
        # by Lingua but below the standalone threshold. Context may resolve an
        # ambiguous English-leading fragment, never a confidently foreign clause.
        def masked_english(p):
            m = mask_longest_term(p)
            return bool(m) and contextual_english(m, detector()(m), whole)

        passes = [
            s["english"]
            or contextual_english(p, s, whole)
            or technical_english_clause(p, whole)
            or (whole["english"] and masked_english(p))
            for p, s in zip(parts, scores)
        ]
        return {
            "confident_english": whole["english"] and all(passes),
            "segments_checked": len(passes),
            "method": "English whole-query threshold (langdetect >=.95 or Lingua >=.80), plus sentence/span checks. Ambiguous fragments need English context and either English ranked first (>=.35), or English >=.15 with two English function-word anchors. Other confident foreign fragments do not inherit context. Complete bounded English arithmetic clauses use an explicit grammar/vocabulary check to resolve technical-term detector errors.",
            "limitation": "Heuristic scores are not calibrated clinical confidence. Short technical phrases can be overblocked; mixed-language text can still be missed.",
        }
    except Exception:
        return {"confident_english": False, "reason": "language_detector_unavailable"}
