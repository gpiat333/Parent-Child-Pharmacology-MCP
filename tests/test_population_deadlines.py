import asyncio
from datetime import date

import httpx
import pytest

from parent_child_pharmacology.mc import parent_resources as p
from parent_child_pharmacology.mc import sources


@pytest.mark.parametrize(
    "elig,status",
    [
        ({}, "unverified"),
        ({"minimumAge": None, "maximumAge": None}, "unverified"),
        ({"minimumAge": "18 Years"}, "adult_only"),
        ({"minimumAge": "17 Years", "maximumAge": "65 Years"}, "pediatric_included"),
        ({"minimumAge": "216 Months"}, "adult_only"),
        ({"minimumAge": "1 Month"}, "pediatric_included"),
        ({"minimumAge": "1 Week"}, "pediatric_included"),
        ({"minimumAge": "2 Days"}, "pediatric_included"),
        ({"minimumAge": "4 Hours"}, "pediatric_included"),
        ({"minimumAge": "30 Minutes"}, "pediatric_included"),
        ({"minimumAge": "N/A"}, "unverified"),
        ({"minimumAge": "-1 Years"}, "unverified"),
        ({"maximumAge": "17 Years"}, "pediatric_included"),
        ({"stdAges": ["CHILD", "ADULT"]}, "unverified"),
        ({"stdAges": ["ADULT"]}, "adult_only"),
        ({"stdAges": "CHILD"}, "unverified"),
        ({"minimumAge": "18 Years", "stdAges": ["CHILD"]}, "unverified"),
        ({"minimumAge": "5 Years", "stdAges": ["ADULT"]}, "unverified"),
        ({"minimumAge": "16 Years", "maximumAge": "5 Years"}, "unverified"),
        ({"minimumAge": "6570 Days"}, "unverified"),
    ],
)
def test_age_field_screening(elig, status):
    result = p.pediatric_population(elig)
    assert result["status"] == status
    assert not result["individual_eligibility_confirmed"]


@pytest.mark.parametrize(
    "deadline,relation,known",
    [
        ("2026-11-20", "future", True),
        ("2026-11-19", "today", True),
        ("2020-01-01", "past", True),
        (None, "unknown", False),
        ("bad", "unknown", False),
        ("2026-02-30", "unknown", False),
    ],
)
def test_deadline_independent_of_meeting_and_submission(deadline, relation, known):
    r = p.input_row(
        {"comments_close_on": deadline, "dates": "The meeting was held in 2020."},
        date(2026, 11, 19),
    )
    assert r["comment_deadline"]["relation_to_as_of"] == relation
    assert r["comment_deadline"]["date_known"] == known
    assert not r["submission_open_confirmed"]
    assert r["submission_status"] == "not_verified"
    assert not r["meeting_dates_used_for_deadline"]


def studies():
    return [
        {
            "protocolSection": {
                "identificationModule": {"nctId": f"NCT0000000{i}", "briefTitle": "Epilepsy study"},
                "statusModule": {"overallStatus": "RECRUITING"},
                "eligibilityModule": elig,
                "conditionsModule": {"conditions": ["Epilepsy"]},
            }
        }
        for i, elig in enumerate(
            [
                {"stdAges": ["CHILD", "ADULT"]},
                {"minimumAge": "18 Years"},
                {"minimumAge": "5 Years", "maximumAge": "17 Years"},
            ],
            1,
        )
    ]


def test_recruiting_withholds_adult_and_unverified_candidates(monkeypatch):
    async def fake(*args, **kwargs):
        return httpx.Response(200, json={"studies": studies()})

    monkeypatch.setattr(p.http, "request", fake)
    r = asyncio.run(p.recruiting_studies("epilepsy", "pediatric", "Canada"))
    assert [s["nct"] for s in r["studies"]] == ["NCT00000003"]
    assert r["excluded_population_counts"] == {"adult_only": 1, "unverified": 1}


def test_legacy_trial_search_cannot_bypass_population_gate(monkeypatch):
    async def fake(*args, **kwargs):
        return httpx.Response(200, json={"studies": studies()})

    monkeypatch.setattr(sources.http, "request", fake)
    r = asyncio.run(sources.trials_search("epilepsy", "pediatric"))
    assert [s["nct"] for s in r] == ["NCT00000003"]


def test_other_population_searches_unchanged(monkeypatch):
    async def fake(*args, **kwargs):
        return httpx.Response(200, json={"studies": studies()})

    monkeypatch.setattr(p.http, "request", fake)
    assert len(asyncio.run(p.recruiting_studies("epilepsy", "any"))["studies"]) == 3
