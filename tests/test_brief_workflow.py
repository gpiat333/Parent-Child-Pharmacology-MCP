"""Behavioral regression for an explicit brief bypassing the composite contract."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from parent_child_pharmacology.core.safety import route
from parent_child_pharmacology.core.workflows import requested_workflow


@pytest.mark.parametrize(
    "question",
    [
        "Prepare a pregnancy evidence brief for daridorexant. Keep empty rows visible. Do not give doses.",
        "Prepare an evidence brief for sertraline during lactation using the medication evidence brief tool.",
        "Please prepare questions for my clinician about sertraline during breastfeeding. Use the evidence brief tool.",
        "Create a pediatric evidence brief for levetiracetam.",
        "Compile an evidence brief for lamotrigine in pregnancy.",
        "Using medication_evidence_brief, summarize sertraline research.",
    ],
)
def test_explicit_brief_request_maps_to_composite_workflow(question):
    # Intent recognition is separate from the conservative language gate.
    assert requested_workflow(question)["required_tool"] == "medication_evidence_brief"


@pytest.mark.parametrize("verb", ["give", "show", "send"])
@pytest.mark.parametrize("recipient", ["", "me "])
def test_brief_delivery_paraphrases_require_composite(verb, recipient):
    question = f"Please {verb} {recipient}a pregnancy evidence brief for lamotrigine."
    assert requested_workflow(question)["required_tool"] == "medication_evidence_brief"


@pytest.mark.parametrize("verb", ["give", "show", "send"])
@pytest.mark.parametrize("negation", ["Do not", "Don't", "Never"])
def test_negated_delivery_paraphrases_do_not_require_composite(verb, negation):
    question = f"{negation} {verb} me an evidence brief. Search LactMed only."
    assert requested_workflow(question) is None


@pytest.mark.parametrize(
    "question",
    [
        "Give me a pregnancy evidence brief for lamotrigine.",
        "Show me a pregnancy evidence brief for lamotrigine.",
        "Send me a pregnancy evidence brief for lamotrigine.",
    ],
)
def test_delivery_paraphrases_pass_whole_question_preflight(question):
    decision = route(question)
    assert decision["allow_research"]
    assert decision["requested_workflow"]["required_tool"] == "medication_evidence_brief"


@pytest.mark.parametrize(
    "suffix",
    [
        "for my little white pill.",
        "for lamotrigine. I want to harm myself with my pills.",
        "for lamotrigine. My baby cannot breathe.",
        "for lamotrigine. Should I stop taking my medicine?",
        "for lamotrigine. Puedo tomar sertralina durante la lactancia.",
    ],
)
def test_delivery_paraphrase_cannot_override_stop(suffix):
    decision = route("Give me a pregnancy evidence brief " + suffix)
    assert not decision["allow_research"]
    assert "requested_workflow" not in decision


@pytest.mark.parametrize("case_id", ["E01-gap", "D05-brief", "D06-clinician-questions"])
def test_existing_evaluation_question_requires_brief_after_full_preflight(case_id):
    cases = json.loads(
        (Path(__file__).parents[1] / "evaluation/program-safety-revision/cases.json").read_text(
            encoding="utf-8"
        )
    )
    question = next(c["question"] for c in cases if c["id"] == case_id)
    decision = route(question)
    assert decision["allow_research"]
    assert decision["requested_workflow"]["required_tool"] == "medication_evidence_brief"


def test_english_language_uncertainty_still_overrides_workflow(monkeypatch):
    from parent_child_pharmacology.core import language

    monkeypatch.setattr(language, "english_confidence", lambda _: {"confident_english": False})
    decision = route("Create a pediatric evidence brief for levetiracetam.")
    assert decision["route"] == "language_support"
    assert not decision["allow_research"] and "requested_workflow" not in decision


@pytest.mark.parametrize(
    "question",
    [
        "What is an evidence brief?",
        "Explain the evidence brief tool.",
        "Search LactMed for sertraline.",
        "Do not use the evidence brief tool. Search LactMed only.",
        "Don't prepare an evidence brief. Find a pregnancy registry.",
        "Use individual source tools instead of the evidence brief.",
        "Skip the medication evidence brief tool and show registry contacts.",
    ],
)
def test_mentions_or_declined_workflows_do_not_force_brief(question):
    assert requested_workflow(question) is None


@pytest.mark.parametrize(
    "question",
    [
        "Prepare an evidence brief for my little white pill.",
        "Prepare an evidence brief. I want to harm myself with my pills.",
        "Prepare an evidence brief. My baby cannot breathe.",
        "Prepare an evidence brief. Should I stop taking my medicine?",
        "Prepare an evidence brief. Puedo tomar sertralina durante la lactancia.",
    ],
)
def test_stop_routes_cannot_be_bypassed_by_workflow_request(question):
    decision = route(question)
    assert not decision["allow_research"]
    assert "requested_workflow" not in decision


def powershell(script):
    helper = Path(__file__).parents[1] / "chat-client/parent-chat-policy.ps1"
    command = ". '" + str(helper).replace("'", "''") + "'\n" + script
    result = subprocess.run(
        [shutil.which("pwsh") or "pwsh", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_client_requires_brief_once_and_releases_optional_tools():
    result = powershell("""
    $d=@{allow_research=$true;requested_workflow=@{required_tool='medication_evidence_brief'}}
    $before=Get-RequiredEvidenceTool $d @('medication_evidence_brief','search_literature') @()
    $after=Get-RequiredEvidenceTool $d @('medication_evidence_brief','search_literature') @(@{tool='medication_evidence_brief'})
    @{before=$before;after=$after} | ConvertTo-Json
    """)
    assert result == {"before": "medication_evidence_brief", "after": None}


@pytest.mark.parametrize(
    "message",
    [
        {"content": "A final answer without retrieval"},
        {"tool_calls": [{"function": {"name": "search_literature"}}]},
        {
            "tool_calls": [
                {"function": {"name": "medication_evidence_brief"}},
                {"function": {"name": "search_literature"}},
            ]
        },
    ],
)
def test_client_rejects_bypass_before_any_optional_retrieval(message):
    encoded = json.dumps(message).replace("'", "''")
    result = powershell(
        "$m='"
        + encoded
        + "' | ConvertFrom-Json; try { Assert-RequiredEvidenceToolCall 'medication_evidence_brief' $m; $false | ConvertTo-Json } catch { $true | ConvertTo-Json }"
    )
    assert result is True


def test_client_accepts_required_call_and_does_not_constrain_other_requests():
    result = powershell("""
    $m=@{tool_calls=@(@{function=@{name='medication_evidence_brief'}})}
    Assert-RequiredEvidenceToolCall 'medication_evidence_brief' $m
    Assert-RequiredEvidenceToolCall '' @{content='An ordinary answer'}
    $true | ConvertTo-Json
    """)
    assert result is True


def test_client_unavailable_workflow_fails_closed_and_stops_take_priority():
    result = powershell("""
    $d=@{allow_research=$true;requested_workflow=@{required_tool='medication_evidence_brief'}}
    $blocked=$false
    try { Get-RequiredEvidenceTool $d @('search_literature') @() } catch { $blocked=$true }
    $d.allow_research=$false
    $stop=Get-RequiredEvidenceTool $d @('search_literature') @()
    @{missing_tool_blocked=$blocked;stop_requirement=$stop} | ConvertTo-Json
    """)
    assert result == {"missing_tool_blocked": True, "stop_requirement": None}
