"""Conservative request routing, not a diagnostic or clinical triage system."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

POLICY = json.loads((Path(__file__).parent / "policy.json").read_text(encoding="utf-8"))

POISON = "https://poisonhelp.hrsa.gov/what-you-can-do"
EMERGENCY = "https://www.poison.org/need-immediate-assistance"
POLICY_VERSION = POLICY["version"]


def identity_is_vague(text):
    return bool(re.search(POLICY["patterns"]["patterns_6"], text, re.I))


def contains_identifiers(text):
    return bool(re.search(POLICY["patterns"]["patterns_7"], text, re.I))


def _clauses(text):
    return [c for c in re.split(r"[.!?;\n]", text) if c.strip()]


def _crisis(q):
    if re.search(POLICY["patterns"]["crisis"], q, re.I):
        return True
    # Naming a perinatal mood condition is a research topic; describing one's
    # own condition still routes to support.
    return any(
        re.search(POLICY["patterns"]["crisis_condition"], c)
        and re.search(POLICY["patterns"]["personal_marker"], c)
        for c in _clauses(q)
    )


def route(question, country="US", *, language_required=True):
    q = question.lower().replace("’", "'")
    result = {
        "source": "local:parent-safety-policy",
        "policy_version": POLICY_VERSION,
        "route": "evidence",
        "allow_research": True,
        "message": None,
        "source_urls": [],
        "limitations": [POLICY["messages"]["messages_2"]],
    }
    # A fixed referral, not a diagnosis, severity score, or model-generated answer.
    if _crisis(q):
        perinatal = bool(re.search(POLICY["patterns"]["perinatal"], q, re.I))
        result.update(
            route="mental_health_support",
            allow_research=False,
            allow_model_answer=False,
            clinical_assessment_performed=False,
        )
        if country.upper() == "US":
            result["message"] = POLICY["messages"]["crisis_us"]
            result["source_urls"] = ["https://988lifeline.org"]
            result["referrals"] = [
                {
                    "name": "988 Suicide & Crisis Lifeline",
                    "call": "988",
                    "text": "988",
                    "phone_link": "tel:988",
                    "sms_link": "sms:988",
                }
            ]
            if perinatal:
                # Fixed strings only: a referral number is never model-generated or paraphrased.
                result["message"] += " " + POLICY["messages"]["maternal_hotline"]
                result["source_urls"].append(
                    "https://mchb.hrsa.gov/national-maternal-mental-health-hotline"
                )
                result["referrals"].append(
                    {
                        "name": "National Maternal Mental Health Hotline (HRSA)",
                        "call": "1-833-852-6262",
                        "text": "1-833-852-6262",
                        "phone_link": "tel:18338526262",
                        "sms_link": "sms:18338526262",
                        "role": "24/7 call or text support for pregnant and postpartum people, in English and Spanish.",
                    }
                )
                result["message"] += " " + POLICY["messages"]["perinatal_support"]
                result["source_urls"].append("https://postpartum.net/get-help/")
                result["referrals"].append(
                    {
                        "name": "Postpartum Support International HelpLine",
                        "call": "1-800-944-4773",
                        "role": "Non-emergency support and resources; callback service, not a crisis line.",
                    }
                )
            if re.search(r"overdos|poison|pills|tablets|bottle", q):
                result["message"] += " " + POLICY["messages"]["messages_8"]
                result["source_urls"].append(POISON)
        else:
            result["message"] = (
                "Please contact local emergency services or a local crisis service for immediate support. This service cannot verify a crisis number for your country. Contact your clinician for perinatal mental-health support."
            )
        return result
    symptom_text = re.sub(POLICY["patterns"]["patterns_1"], "", q)
    # A named aggregate outcome is not itself a report of an active symptom.
    # Never use a "research" declaration to bypass a personal/acute concern,
    # and leave any separate symptom clause intact for the urgent matcher.
    clauses = re.split(r"([.!?;\n])", symptom_text)
    for i, clause in enumerate(clauses):
        if not re.search(
            r"\b(?:i|my|our|your|we|now|currently|today|tonight|help|emergency)\b", clause
        ):
            clauses[i] = re.sub(
                r"\b(?:control of seizures|seizure(?:s)? (?:control|frequency|outcomes))\b",
                "aggregate outcome",
                clause,
            )
    joined = "".join(clauses)
    # Event wording ("is having a seizure") is always urgent. A condition name
    # alone ("levetiracetam for seizures") is a research topic unless the same
    # clause also signals an acute situation ("seizures now", "help").
    urgent = re.search(POLICY["patterns"]["patterns_2"], joined) or any(
        re.search(POLICY["patterns"]["urgent_condition"], c)
        and re.search(POLICY["patterns"]["acute_marker"], c)
        for c in _clauses(joined)
    )
    poison = re.search(POLICY["patterns"]["patterns_3"], q)
    # Negative educational statements must not suppress a second actual symptom.
    if urgent or poison:
        result.update(
            route="urgent_help" if urgent else "poison_help",
            allow_research=False,
            allow_model_answer=False,
            clinical_assessment_performed=False,
        )
        if country.upper() == "US":
            result["message"] = POLICY["messages"]["messages_12"] + POLICY["messages"]["messages_8"]
        else:
            result["message"] = POLICY["messages"]["messages_3"]
        result["source_urls"] = [EMERGENCY, POISON]
        return result
    if contains_identifiers(question):
        result.update(
            route="privacy", allow_research=False, message=POLICY["messages"]["messages_9"]
        )
        return result
    # Exclude common instruction suffixes; they are not requests for dosing.
    # Remove only the explicit exclusion, never the remainder of the question.
    # A second actual request ("...but what dose should I give?") stays visible.
    intent = re.sub(POLICY["patterns"]["patterns_4"], "", q)
    if re.search(POLICY["patterns"]["patterns_5"], intent):
        result.update(
            route="clinician_or_pharmacist",
            allow_research=False,
            message=POLICY["messages"]["messages_10"],
        )
        return result
    if identity_is_vague(q):
        result.update(
            route="confirm_identity",
            allow_research=False,
            requires_confirmation=True,
            message=POLICY["messages"]["messages_11"],
        )
        return result
    if language_required:
        from .language import english_confidence

        result["language_gate"] = english_confidence(question)
        if not result["language_gate"]["confident_english"]:
            result.update(
                route="language_support",
                allow_research=False,
                allow_model_answer=False,
                message=POLICY["messages"]["language_support"],
            )
    if result["allow_research"]:
        from .workflows import requested_workflow

        workflow = requested_workflow(question)
        if workflow:
            result["requested_workflow"] = workflow
    return result


def envelope(out):
    """Add portable limits to every tool; clients must enforce the response policy."""
    return {
        "policy_version": POLICY_VERSION,
        "scope": POLICY["messages"]["messages_1"],
        "requires_identity_confirmation": bool(
            out.get("requires_confirmation") or out.get("found") is False
        ),
        "evidence_unavailable": bool(out.get("error")),
        "rules": [
            "Do not infer safety, drug identity, or absence of evidence from missing or empty results.",
            POLICY["messages"]["messages_4"],
            POLICY["messages"]["messages_5"],
            POLICY["messages"]["messages_6"],
            POLICY["messages"]["messages_7"],
        ],
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "client_enforcement_required": True,
    }
