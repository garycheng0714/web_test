from unittest.mock import MagicMock

from typesafe_sdk import Noul

from web_test.planning.review import ReviewRequest, Verdict, build_request, run_review
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


def test_build_request_asks_groundedness_only():
    request = build_request("# PRD", _design())

    assert isinstance(request, ReviewRequest)
    assert set(request.questions) == {"grounded_1", "grounded_2", "grounded_3"}
    assert request.state.prd == "# PRD"
    assert request.state.cases[0].index == 1
    assert request.state.cases[0].steps == ["Go -> Page shown"]
    assert isinstance(request.questions["grounded_1"], Noul)


def test_run_review_returns_the_verdicts():
    result = run_review("# PRD", _design(), system_one=lambda request: DECISIONS)

    assert result == DECISIONS


def test_run_review_returns_none_when_the_call_fails():
    system_one = MagicMock(side_effect=RuntimeError("no key"))

    assert run_review("# PRD", _design(), system_one=system_one) is None


def test_run_review_returns_none_on_empty_answers():
    assert run_review("# PRD", _design(), system_one=lambda request: {}) is None
