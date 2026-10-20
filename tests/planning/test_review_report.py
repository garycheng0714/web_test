from web_test.planning.review import Verdict
from web_test.planning.review_report import render_report
from web_test.planning.schema import Case, DesignOutput

DECISIONS = {
    "ac_1": Verdict(True, 0.95),
    "ac_2": Verdict(False, 0.05),
    "ac_3": Verdict(True, 0.55),
    "step_1_1_reasonable": Verdict(True, 0.95),
    "step_1_1_complete": Verdict(True, 0.95),
    "step_1_1_observable": Verdict(True, 0.95),
    "step_2_1_reasonable": Verdict(True, 0.9),
    "step_2_1_complete": Verdict(False, 0.1),
    "step_2_1_observable": Verdict(True, 0.9),
    "step_3_1_reasonable": Verdict(True, 0.95),
    "step_3_1_complete": Verdict(True, 0.95),
    "step_3_1_observable": Verdict(True, 0.55),
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


def test_render_report_summarises_checks_findings_and_low_confidence():
    text = render_report(DECISIONS, _design())

    assert "**AC alignment:** 2/3 cases aligned" in text
    assert "**Step quality:** 3/3 reasonable, 2/3 complete, 3/3 observable" in text
    assert "Case 2: B (AC alignment, p=0.05)" in text
    assert "Case 2, step 1: Go (complete, p=0.1)" in text
    assert "Case 3: C (AC alignment, confidence=0.55)" in text
    assert "Case 3, step 1: Go (observable, confidence=0.55)" in text
    assert "Advisory" in text


def test_render_report_shows_none_when_clean():
    clean = {
        "ac_1": Verdict(True, 0.95),
        "ac_2": Verdict(True, 0.95),
        "ac_3": Verdict(True, 0.95),
        "step_1_1_reasonable": Verdict(True, 0.95),
        "step_1_1_complete": Verdict(True, 0.95),
        "step_1_1_observable": Verdict(True, 0.95),
        "step_2_1_reasonable": Verdict(True, 0.95),
        "step_2_1_complete": Verdict(True, 0.95),
        "step_2_1_observable": Verdict(True, 0.95),
        "step_3_1_reasonable": Verdict(True, 0.95),
        "step_3_1_complete": Verdict(True, 0.95),
        "step_3_1_observable": Verdict(True, 0.95),
    }

    text = render_report(clean, _design())

    assert "**AC alignment:** 3/3 cases aligned" in text
    assert "**Step quality:** 3/3 reasonable, 3/3 complete, 3/3 observable" in text
    assert "**Findings**\n\nNone." in text
    assert "**Needs review (confidence < 0.8)**\n\nNone." in text


def test_render_report_ignores_unknown_question_ids():
    decisions = {"ac_1": Verdict(True, 0.95), "surprise": Verdict(False, 0.01)}

    text = render_report(decisions, _design())

    assert "**AC alignment:** 1/3 cases aligned" in text
    assert "**Step quality:** 0/3 reasonable, 0/3 complete, 0/3 observable" in text
    assert "surprise" not in text
