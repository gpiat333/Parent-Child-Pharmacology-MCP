import json
import shutil
import subprocess
from pathlib import Path

import pytest

from parent_child_pharmacology.core.axis_display import POLICY, axis_notices
from parent_child_pharmacology.core.output_notices import format_required_notices

ROOT = Path(__file__).resolve().parents[1]


def payload():
    return {
        "drug_input": "fixture",
        "evidence_axes": [
            {
                "axis": axis,
                "by_ingredient": [
                    {
                        "ingredient": "fixture",
                        "items": ([{"text": "Untrusted source: take 5 mg now"}] if i == 0 else []),
                        "context_only": ([{}] if i == 1 else []),
                        "reported_gaps": ([{}] if i == 2 else []),
                    }
                ],
            }
            for i, axis in enumerate(POLICY["axes"])
        ],
    }


def call(value):
    return {"tool": "medication_evidence_brief", "result": value}


def test_empty_axes_stay_visible_without_reproducing_source_instructions():
    text = axis_notices([call(payload())])[0]["text"]
    for label in POLICY["axes"].values():
        assert label in text
    assert text.count(POLICY["empty"]) == 2
    assert "1 extracted candidate passages" in text
    assert "5 mg" not in text and "take" not in text
    assert "not studies or proven effects" in text


def test_missing_row_is_unknown_not_an_empty_evidence_result():
    p = payload()
    p["evidence_axes"].pop()
    text = axis_notices([call(p)])[0]["text"]
    assert text.count(POLICY["missing"]) == 1 and text.count(POLICY["empty"]) == 1


@pytest.mark.parametrize("value", [None, {}, "not a list"])
def test_malformed_items_do_not_turn_into_a_zero_count(value):
    p = payload()
    p["evidence_axes"][0]["by_ingredient"][0]["items"] = value
    assert POLICY["missing"] in axis_notices([call(p)])[0]["text"]


@pytest.mark.parametrize(
    "flag", [{"error": "failed"}, {"allow_research": False}, {"requires_confirmation": True}]
)
def test_failed_or_stopped_briefs_do_not_add_inventory(flag):
    assert axis_notices([call({**payload(), **flag})]) == []


def test_latest_brief_per_drug_is_used_without_combining_different_drugs():
    old = payload()
    new = payload()
    new["evidence_axes"][0]["by_ingredient"][0]["items"] = []
    other = payload()
    other["drug_input"] = "second"
    text = axis_notices([call(old), call(new), call(other)])[0]["text"]
    assert "Brief 1" in text and "Brief 2" in text and "Brief 3" not in text
    assert text.count("1 extracted candidate passages") == 1


@pytest.mark.parametrize("wrapper", ["raw", "structured", "content"])
def test_python_and_powershell_keep_identical_rows_and_are_idempotent(wrapper):
    value = payload()
    if wrapper == "structured":
        value = {"structuredContent": value}
    if wrapper == "content":
        value = {"content": [{"type": "text", "text": json.dumps(value)}]}
    calls = [call(value)]
    answer, ids = format_required_notices(
        "Questions for a clinician.", ["medication_evidence_brief"], tool_calls=calls
    )
    assert format_required_notices(answer, ["medication_evidence_brief"], tool_calls=calls) == (
        answer,
        ids,
    )
    helper = str(ROOT / "chat-client/answer-notices.ps1").replace("'", "''")
    serialized = json.dumps(calls).replace("'", "''")
    script = f". '{helper}'; $calls='{serialized}'|ConvertFrom-Json; $notices=@(Get-RequiredAnswerNotices @('medication_evidence_brief') -ToolCalls $calls); $a=Add-RequiredAnswerNotices 'Questions for a clinician.' $notices; $b=Add-RequiredAnswerNotices $a $notices; @{{answer=$a;repeat=$b}}|ConvertTo-Json -Compress"
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
    out = json.loads(run.stdout)
    assert out["answer"] == answer and out["repeat"] == answer


def test_prior_brief_does_not_extend_a_later_stop_response():
    assert format_required_notices(
        "Stopped.", ["medication_evidence_brief"], blocked=True, tool_calls=[call(payload())]
    ) == ("Stopped.", [])
