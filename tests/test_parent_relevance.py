from parent_child_pharmacology.mc.parent_resources import topic_support


def test_broad_notice_does_not_claim_pediatric_fit():
    r = topic_support("pediatric research", {"title": "Cancer research forms", "abstract": None})
    assert r["assessment"] == "indirect_or_unverified"
    assert r["missing_words"] == ["pediatric"]


def test_keywords_record_their_actual_fields_not_suitability():
    r = topic_support("eczema", {"title": "Infant microbiome study", "conditions": "eczema"})
    assert r["matched_words_by_field"] == {"title": [], "conditions": ["eczema"]}
    assert not r["clinical_suitability_confirmed"]


def test_substrings_do_not_confirm_topic():
    assert (
        topic_support("child", {"title": "Childhood research"})["assessment"]
        == "indirect_or_unverified"
    )
