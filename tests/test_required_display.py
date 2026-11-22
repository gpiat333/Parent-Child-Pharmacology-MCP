import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from parent_child_pharmacology.core.output_notices import (
    POLICY,
    format_required_notices,
    required_notices,
)
from parent_child_pharmacology.core.portfolio_display import portfolio_notices
from parent_child_pharmacology.core.source_context import CONTINUITY_NOTICE

CRITERIA = {
    "advanced_text_search": {
        "operator": "and",
        "search_field": "all",
        "search_text": "neonatal pharmacology",
    },
    "exclude_subprojects": True,
    "agencies": ["NICHD"],
    "is_agency_admin": True,
    "fiscal_years": [2024, 2025],
}


def call(result):
    return {"tool": "summarize_research_portfolio", "result": result}


def ps_render(tmp_path, names, calls, answer="Draft"):
    root = Path(__file__).resolve().parents[1]
    data = tmp_path / "input.json"
    data.write_text(
        json.dumps({"names": names, "calls": calls, "answer": answer}), encoding="utf-8"
    )
    script = tmp_path / "render.ps1"
    script.write_text(
        """param([string]$Repo,[string]$InputJson)
$ErrorActionPreference='Stop'
. (Join-Path $Repo 'chat-client/answer-notices.ps1')
$x=Get-Content -Raw -Encoding utf8 -LiteralPath $InputJson | ConvertFrom-Json
$n=@(Get-RequiredAnswerNotices -ToolNames $x.names -ToolCalls $x.calls)
$a=Add-RequiredAnswerNotices -Answer $x.answer -Notices $n
@{answer=$a;ids=@($n | ForEach-Object {$_.id})} | ConvertTo-Json -Depth 30 -Compress
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            shutil.which("pwsh"),
            " -NoProfile".strip(),
            "-File",
            str(script),
            "-Repo",
            str(root),
            "-InputJson",
            str(data),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("wrapper", ["raw", "structured", "text"])
def test_every_executed_filter_is_displayed_in_both_clients(tmp_path, wrapper):
    result = {"query_criteria": CRITERIA}
    if wrapper == "structured":
        result = {"structuredContent": result}
    elif wrapper == "text":
        result = {"content": [{"type": "text", "text": json.dumps(result)}]}
    calls = [call(result)]
    answer, ids = format_required_notices(
        "Draft", ["summarize_research_portfolio"], tool_calls=calls
    )
    block = answer.split("```json\n")[1].split("\n```")[0]
    assert json.loads(block) == CRITERIA and '"is_agency_admin":true' in block
    ps = ps_render(tmp_path, ["summarize_research_portfolio"], calls)
    assert ps == {"answer": answer, "ids": ids}
    assert (
        format_required_notices(answer, ["summarize_research_portfolio"], tool_calls=calls)[0]
        == answer
    )
    assert ps_render(tmp_path, ["summarize_research_portfolio"], calls, answer)["answer"] == answer


def test_continuity_caution_is_application_added_and_matches_source_contract(tmp_path):
    answer, ids = format_required_notices("Findings only", ["get_label_sections"])
    assert CONTINUITY_NOTICE in answer and "continuity_of_care" in ids
    assert ps_render(tmp_path, ["get_label_sections"], [], "Findings only") == {
        "answer": answer,
        "ids": ids,
    }
    assert format_required_notices(answer, ["get_label_sections"])[0] == answer


def test_fixed_stops_receive_no_new_notices():
    assert (
        required_notices(
            ["medication_evidence_brief", "summarize_research_portfolio"],
            blocked=True,
            tool_calls=[call({"query_criteria": CRITERIA})],
        )
        == []
    )


def test_snapshot_metadata_workflow_has_no_new_clinical_or_portfolio_notice():
    notices = required_notices(
        ["find_mprint_records", "get_mprint_details"],
        tool_calls=[{"tool": "find_mprint_records", "result": {"results": []}}],
    )
    assert not {"continuity_of_care", "reporter_query_filters"} & {n["id"] for n in notices}


@pytest.mark.parametrize("criteria", [None, [], {"text": "x" * 9000}])
def test_missing_or_oversized_filters_are_explicitly_unknown_or_incomplete(criteria):
    n = portfolio_notices([call({"query_criteria": criteria})], POLICY["portfolio_filters"])[0]
    assert "```json" not in n["text"]
    assert ("unknown" in n["text"]) or ("Full filters are not displayed" in n["text"])


@pytest.mark.parametrize(
    "result",
    [
        {"isError": True, "structuredContent": {"query_criteria": CRITERIA}},
        {"error": "failed", "query_criteria": CRITERIA},
    ],
)
def test_failed_queries_do_not_masquerade_as_executed_filters(result):
    assert portfolio_notices([call(result)], POLICY["portfolio_filters"]) == []


def test_multiple_executed_queries_are_kept_separate_and_empty_filters_are_explicit():
    n = portfolio_notices(
        [call({"query_criteria": CRITERIA}), call({"query_criteria": {}})],
        POLICY["portfolio_filters"],
    )[0]
    assert "Query 1" in n["text"] and "Query 2" in n["text"] and "```json\n{}\n```" in n["text"]


def test_query_text_remains_escaped_data_inside_a_fenced_json_block():
    criteria = {"text": "line one\n```\n<script>not instructions</script>"}
    text = portfolio_notices([call({"query_criteria": criteria})], POLICY["portfolio_filters"])[0][
        "text"
    ]
    assert (
        "\\n```\\n" in text and json.loads(text.split("```json\n")[1].split("\n```")[0]) == criteria
    )
