"""Pediatric evidence briefs use pediatric axes, in the server and in both chat clients."""

import asyncio
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from parent_child_pharmacology.core.axis_display import POLICY, axis_notices
from parent_child_pharmacology.core.evidence_axes import PEDIATRIC_AXES, build_pediatric_axes
from parent_child_pharmacology.core.output_notices import format_required_notices

ROOT = Path(__file__).resolve().parents[1]

PEDIATRIC_USE = (
    "The safety and effectiveness of exampledrug in patients 1 month to 16 years of age have been established. "
    "Safety and effectiveness in pediatric patients below the age of 1 month have not been established. "
    "Clearance in children was 40% higher than in adults. "
    "A randomized trial in 98 pediatric patients observed aggressive behavior in some children. "
    "Studies in juvenile rats did not demonstrate adverse effects on postnatal development."
)


def row():
    return {
        "label": {
            "url": "https://dailymed.example/label",
            "sections": {"pediatric_use": PEDIATRIC_USE},
        },
        "pediatric_labeling_changes": {
            "results": [
                {
                    "labeling_change_date": "2025-06-27",
                    "trade_name": "Exampledrug tablets",
                    "legislation": "PREA Only",
                    "indication": "Partial-onset seizures",
                    "labeling_change_summary": "Tube administration added.",
                    "url": "https://fda.example/pediatric",
                }
            ]
        },
        "literature": {
            "articles": [
                {
                    "pmid": "123",
                    "abstract": "In infants, the half-life was 6 hours. Adults tolerated it well.",
                }
            ]
        },
        "adverse_events": {},
    }


def axes_by_key():
    return {a["axis"]: a for a in build_pediatric_axes(row(), "child")}


def test_pediatric_axes_sort_label_changes_and_abstracts():
    axes = axes_by_key()
    assert list(axes) == list(PEDIATRIC_AXES)
    labeling = axes["pediatric_labeling"]
    assert any("have been established" in i["text"] for i in labeling["items"])
    assert any("FDA Pediatric Labeling Changes" == i["source"] for i in labeling["items"])
    assert any("not been established" in g["text"] for g in labeling["reported_gaps"])
    exposure = axes["pediatric_exposure"]["items"]
    assert any("Clearance in children" in i["text"] for i in exposure)
    assert any(i.get("pmid") == "123" and "half-life" in i["text"] for i in exposure)
    effects = axes["pediatric_effectiveness_safety"]
    assert any("randomized trial" in i["text"] for i in effects["items"])
    assert any(i["study_context"] == "animal" for i in effects["context_only"])
    # Adult-only sentences from abstracts are not attributed to children.
    assert not any("Adults tolerated" in i["text"] for a in axes.values() for i in a["items"])


def test_dose_text_is_flagged_never_a_personal_dose():
    r = row()
    r["label"]["sections"]["pediatric_use"] = (
        "A trial in children used a target dose of 60 mg/kg/day."
    )
    item = axes_by_key_from(r)["pediatric_effectiveness_safety"]["items"][0]
    assert item["contains_dose_text"] is True
    assert "never a personal dose" in item["dose_text_notice"]


def axes_by_key_from(r):
    return {a["axis"]: a for a in build_pediatric_axes(r, "child")}


def test_empty_pediatric_axes_say_not_evidence_of_safety():
    empty = {a["axis"]: a for a in build_pediatric_axes({}, "infant")}
    for axis in empty.values():
        assert axis["state"] == "none_retrieved"
        assert "not evidence of safety" in axis["empty_message"]


def brief_payload():
    return {
        "drug_input": "exampledrug",
        "axis_set": "pediatric",
        "evidence_axes": [
            {
                "axis": key,
                "by_ingredient": [
                    {"items": [{}] if i == 0 else [], "context_only": [], "reported_gaps": []}
                ],
            }
            for i, key in enumerate(PEDIATRIC_AXES)
        ],
    }


def call(value):
    return {"tool": "medication_evidence_brief", "result": value}


def test_display_uses_pediatric_labels_for_pediatric_briefs():
    text = axis_notices([call(brief_payload())])[0]["text"]
    for label in POLICY["pediatric_axes"].values():
        assert label in text
    for label in POLICY["axes"].values():
        assert label not in text
    assert POLICY["missing"] not in text


def test_pediatric_display_policy_matches_server_axes():
    assert POLICY["pediatric_axes"] == PEDIATRIC_AXES


def test_brief_selects_pediatric_axes_for_child_population(monkeypatch):
    from parent_child_pharmacology.services import composite, nichd

    async def norm(drug):
        return {"found": True, "ingredients": ["exampledrug"], "requires_confirmation": False}

    async def label(name):
        return row()["label"]

    async def changes(name):
        return row()["pediatric_labeling_changes"]

    async def literature(*a, **k):
        return {"results": [], "abstract_coverage": None}

    async def empty(*a, **k):
        return {}

    async def bpca(*a, **k):
        return {"results": [{"title": "Exampledrug PTN summary"}]}

    monkeypatch.setattr(composite.src, "rxnorm_normalize", norm)
    monkeypatch.setattr(composite, "get_label_sections", label)
    monkeypatch.setattr(composite, "search_pediatric_labeling_changes", changes)
    monkeypatch.setattr(composite, "search_literature", literature)
    monkeypatch.setattr(composite, "get_adverse_event_signals", empty)
    monkeypatch.setattr(composite, "search_trials", empty)
    monkeypatch.setattr(composite, "get_patient_education", empty)
    monkeypatch.setattr(nichd, "search_bpca_evidence", bpca)
    out = asyncio.run(composite.medication_evidence_brief("exampledrug", "child"))
    assert out["axis_set"] == "pediatric"
    assert out["evidence_axis_order"] == list(PEDIATRIC_AXES)
    assert [a["axis"] for a in out["evidence_axes"]] == list(PEDIATRIC_AXES)
    assert out["ingredient_evidence"][0]["bpca_study_summaries"]["results"]


@pytest.mark.parametrize("wrapper", ["raw", "structured"])
def test_python_and_powershell_render_identical_pediatric_rows(wrapper):
    value = brief_payload()
    if wrapper == "structured":
        value = {"structuredContent": value}
    calls = [call(value)]
    answer, _ = format_required_notices(
        "Questions for a clinician.", ["medication_evidence_brief"], tool_calls=calls
    )
    assert "Effectiveness and safety findings in children" in answer
    helper = str(ROOT / "chat-client/answer-notices.ps1").replace("'", "''")
    serialized = json.dumps(calls).replace("'", "''")
    script = f". '{helper}'; $calls='{serialized}'|ConvertFrom-Json; $notices=@(Get-RequiredAnswerNotices @('medication_evidence_brief') -ToolCalls $calls); $a=Add-RequiredAnswerNotices 'Questions for a clinician.' $notices; @{{answer=$a}}|ConvertTo-Json -Compress"
    run = subprocess.run(
        [
            shutil.which("pwsh") or pytest.skip("PowerShell (pwsh) is not installed"),
            "-NoProfile",
            "-Command",
            script,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    assert json.loads(run.stdout)["answer"] == answer
