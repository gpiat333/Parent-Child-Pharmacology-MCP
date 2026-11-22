"""Required caveats survive omitted model text and never extend stop responses."""

import asyncio
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from parent_child_pharmacology.core.audit import audited
from parent_child_pharmacology.core.output_notices import format_required_notices, required_notices

ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize(
    "tools,expected",
    [
        (["summarize_research_portfolio"], ["portfolio_interpretation"]),
        (["search_funded_research"], ["portfolio_interpretation"]),
        (["get_label_sections"], ["clinical_framing_review"]),
        (["get_lactmed_record", "get_label_sections"], ["clinical_framing_review"]),
        (["medication_evidence_brief"], ["faers_population_scope", "clinical_framing_review"]),
        (["get_adverse_event_signals"], ["faers_population_scope", "clinical_framing_review"]),
        (
            ["summarize_research_portfolio", "get_abstracts"],
            ["portfolio_interpretation", "clinical_framing_review"],
        ),
        (["route_parent_question", "normalize_drug"], []),
        (["find_recruiting_studies", "get_reporting_resources"], []),
    ],
)
def test_notices_follow_tool_scope(tools, expected):
    assert [n["id"] for n in required_notices(tools)] == expected


def test_caveats_added_once_without_altering_source_text():
    original = "The retrieved portfolio contains 20 records. [S1](https://example.gov/p)"
    answer, ids = format_required_notices(
        original, ["summarize_research_portfolio", "get_label_sections"]
    )
    assert answer.startswith(original + "\n\nApplication limits:")
    assert (
        "research success" in answer and "Human clinical framing review remains required." in answer
    )
    assert format_required_notices(
        answer, ["summarize_research_portfolio", "get_label_sections"]
    ) == (answer, ids)


def test_quoted_notice_is_not_mistaken_for_a_standing_notice():
    notice = required_notices(["get_label_sections"])[0]["text"]
    answer, _ = format_required_notices('Do not say "' + notice + '".', ["get_label_sections"])
    assert answer.endswith("\n" + notice)


def test_stop_response_is_unchanged_even_after_prior_retrieval():
    assert format_required_notices(
        "Confirm the medicine identity.", ["medication_evidence_brief"], blocked=True
    ) == ("Confirm the medicine identity.", [])


@pytest.mark.parametrize("blocked", [False, True])
def test_tool_payload_exposes_required_notice_only_on_allowed_result(blocked):
    async def summarize_research_portfolio():
        return {"projects": [], **({"allow_research": False} if blocked else {})}

    out = asyncio.run(audited(summarize_research_portfolio)())
    assert [n["id"] for n in out["required_display_notices"]] == (
        [] if blocked else ["portfolio_interpretation"]
    )


@pytest.mark.parametrize(
    "tools,blocked",
    [
        (["summarize_research_portfolio"], False),
        (["get_label_sections", "get_lactmed_record"], False),
        (["summarize_research_portfolio", "medication_evidence_brief"], False),
        (["medication_evidence_brief"], True),
        (["route_parent_question"], False),
    ],
)
def test_powershell_and_python_clients_render_identical_fixed_contract(tools, blocked):
    helper = str(ROOT / "chat-client/answer-notices.ps1").replace("'", "''")
    payload = json.dumps({"tools": tools, "blocked": blocked}).replace("'", "''")
    script = f""". '{helper}'
    $p='{payload}' | ConvertFrom-Json
    $n=@(Get-RequiredAnswerNotices $p.tools -Blocked:$p.blocked)
    $a=Add-RequiredAnswerNotices 'Saved source answer.' $n
    $b=Add-RequiredAnswerNotices $a $n
    @{{answer=$a;repeat=$b;ids=@($n | ForEach-Object {{ $_.id }})}} | ConvertTo-Json -Compress
    """
    run = subprocess.run(
        [shutil.which("pwsh") or "pwsh", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert run.returncode == 0, run.stderr
    actual = json.loads(run.stdout)
    answer, ids = format_required_notices("Saved source answer.", tools, blocked)
    assert actual == {"answer": answer, "repeat": answer, "ids": ids}


def test_unknown_notice_data_cannot_be_used_as_an_instruction():
    assert required_notices(["ignore_previous_instructions"]) == []
    notice = required_notices(["summarize_research_portfolio"])[0]
    notice["text"] = "Injected text"
    assert required_notices(["summarize_research_portfolio"])[0]["text"] != "Injected text"
