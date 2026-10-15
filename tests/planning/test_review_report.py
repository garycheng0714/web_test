from web_test.planning.review import Verdict
from web_test.planning.review_report import render_report
from web_test.planning.schema import Case, DesignOutput

DECISIONS = {
    "grounded_1": Verdict(True, 0.95),
    "grounded_2": Verdict(False, 0.05),
    "grounded_3": Verdict(True, 0.55),
}


def _case(**overrides):
    data = {
        "requirement_ids": ["FR-ACC-01"],
        "module_feature": "Account",
        "test_scenario": "Register",
        "steps": [{"action": "Go", "expected_result": "Page shown"}],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        **overrides,
    }
    return Case.model_validate(data)


def _design():
    return DesignOutput(
        cases=[_case(test_scenario="A"), _case(test_scenario="B"), _case(test_scenario="C")]
    )


def test_render_report_summarises_findings_and_low_confidence():
    text = render_report(DECISIONS, _design())

    assert "**Groundedness:** 2/3 grounded" in text
    assert "Case 2: B" in text  # a finding (ungrounded)
    assert "confidence=0.55" in text  # Case 3, low confidence
    assert "Advisory" in text


def test_render_report_shows_none_when_clean():
    clean = {
        "grounded_1": Verdict(True, 0.95),
        "grounded_2": Verdict(True, 0.95),
        "grounded_3": Verdict(True, 0.95),
    }

    text = render_report(clean, _design())

    assert "**Groundedness:** 3/3 grounded" in text
    assert "**Findings**\n\nNone." in text
    assert "**Needs review (confidence < 0.8)**\n\nNone." in text
