"""Source warnings are reported as the source's statements, not as the assistant's instructions."""

from pathlib import Path

from parent_child_pharmacology.core.evidence import SOURCE_ATTRIBUTION_RULE, annotate
from parent_child_pharmacology.core.instructions import INSTRUCTIONS

ROOT = Path(__file__).resolve().parents[1]


def test_evidence_results_carry_the_attribution_rule():
    out = annotate({"source": "test", "sections": {}})
    assert out["framing_contract"]["source_attribution"] == SOURCE_ATTRIBUTION_RULE
    assert "The label states that" in SOURCE_ATTRIBUTION_RULE
    assert "name only the contacts the results name" in SOURCE_ATTRIBUTION_RULE


def test_stopped_results_do_not_get_research_framing():
    out = annotate({"source": "test", "allow_research": False})
    assert "framing_contract" not in out


def test_server_and_shared_client_instructions_include_the_rule():
    assert "The label states that" in INSTRUCTIONS
    shared = (ROOT / "chat-client/exposure-presentation-instructions.txt").read_text(
        encoding="utf-8"
    )
    assert "never restated in your own voice as an instruction to the reader" in shared
    assert "name only the contacts the retrieved results name" in shared
