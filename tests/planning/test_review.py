from unittest.mock import MagicMock

from typesafe_sdk import Noul, NoulAnswer

import web_test.planning.review.service as review_module
from web_test.planning.review import JEV_MODEL, JevAnswer, ReviewRequest, ReviewStep, run_review
from web_test.planning.review.questions import STEP_QUALITY_DIMENSIONS
from web_test.planning.review.jev import _normalize
from web_test.planning.review.verification import VerificationStatus, digest_text
from web_test.planning.schema import Case, DesignOutput



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


def _question_ids() -> list[str]:
    ids = [f"ac_{index}" for index in range(1, 4)]
    ids += [
        f"step_{case_index}_1_{check}"
        for case_index in range(1, 4)
        for check in STEP_QUALITY_DIMENSIONS
    ]
    return ids


def _passing_answers() -> dict[str, JevAnswer]:
    return {question_id: JevAnswer(0.95) for question_id in _question_ids()}


def test_run_review_builds_the_three_checks():
    captured = {}

    def system_one(request):
        captured["request"] = request
        return {question_id: JevAnswer(0.95) for question_id in request.questions}

    run_review("# PRD", _design(), "artifact", system_one=system_one)
    request = captured["request"]

    assert isinstance(request, ReviewRequest)
    assert set(request.questions) == set(_question_ids())
    assert request.subject.prd == "# PRD"
    assert request.subject.cases[0].index == 1
    assert request.subject.cases[0].steps == [
        ReviewStep(index=1, action="Go", expected_result="Page shown")
    ]
    assert isinstance(request.questions["ac_1"], Noul)


def test_run_review_aggregates_step_case_and_file_verdicts():
    answers = _passing_answers()
    answers["ac_2"] = JevAnswer(0.05)
    answers["step_3_1_complete"] = JevAnswer(0.6)

    record = run_review("# PRD", _design(), "artifact", system_one=lambda request: answers)

    assert record.result.status is VerificationStatus.FAIL
    assert record.result.cases[1].status is VerificationStatus.FAIL
    assert record.result.cases[2].status is VerificationStatus.NEEDS_REVIEW
    assert record.result.steps[2].status is VerificationStatus.NEEDS_REVIEW
    assert record.result.steps[1].status is VerificationStatus.PASS
    assert next(check for check in record.result.checks if check.question_id == "ac_2").status is (
        VerificationStatus.FAIL
    )


def test_run_review_marks_missing_answers_blocked():
    record = run_review(
        "# PRD",
        _design(),
        "artifact",
        system_one=lambda request: {"ac_1": JevAnswer(0.95)},
    )

    assert record.result.status is VerificationStatus.BLOCKED
    assert record.result.cases[0].status is VerificationStatus.BLOCKED
    assert any(check.status is VerificationStatus.BLOCKED for check in record.result.checks)


def test_blocked_dominates_needs_review():
    answers = _passing_answers()
    answers.pop("step_1_1_observable")
    answers["step_1_1_complete"] = JevAnswer(0.6)

    record = run_review("# PRD", _design(), "artifact", system_one=lambda request: answers)

    assert record.result.steps[0].status is VerificationStatus.BLOCKED
    assert record.result.cases[0].status is VerificationStatus.BLOCKED
    assert record.result.status is VerificationStatus.BLOCKED


def test_fail_dominates_blocked():
    record = run_review(
        "# PRD",
        _design(),
        "artifact",
        system_one=lambda request: {"ac_1": JevAnswer(0.05)},
    )

    assert record.result.cases[0].status is VerificationStatus.FAIL
    assert record.result.status is VerificationStatus.FAIL


def test_unknown_answers_only_are_blocked_with_a_reason():
    record = run_review(
        "# PRD",
        _design(),
        "artifact",
        system_one=lambda request: {"surprise": JevAnswer(0.95)},
    )

    assert record.result.status is VerificationStatus.BLOCKED
    assert record.result.blocked_reason == "No answer was returned for any check."


def test_question_set_version_failure_is_blocked(monkeypatch):
    def _boom(questions):
        raise ValueError("bad question set")

    monkeypatch.setattr(review_module, "question_set_version", _boom)

    record = run_review(
        "# PRD", _design(), "artifact", system_one=lambda request: _passing_answers()
    )

    assert record.result.status is VerificationStatus.BLOCKED
    assert "request build failed" in (record.result.blocked_reason or "")


def test_run_review_returns_blocked_when_the_call_fails():
    record = run_review(
        "# PRD",
        _design(),
        "artifact",
        system_one=MagicMock(side_effect=RuntimeError("no key")),
    )

    assert record.result.status is VerificationStatus.BLOCKED
    assert "Jev call failed" in (record.result.blocked_reason or "")
    assert all(check.status is VerificationStatus.BLOCKED for check in record.result.checks)


def test_run_review_returns_blocked_on_empty_answers():
    record = run_review("# PRD", _design(), "artifact", system_one=lambda request: {})

    assert record.result.status is VerificationStatus.BLOCKED
    assert record.result.blocked_reason == "Jev returned no answers"


def test_record_binds_digests_model_and_question_set():
    record = run_review(
        "# PRD",
        _design(),
        "artifact",
        system_one=lambda request: _passing_answers(),
    )

    assert record.binding.prd_digest == digest_text("# PRD")
    assert record.binding.test_case_digest == digest_text("artifact")
    assert record.binding.model == JEV_MODEL
    assert record.binding.question_set_version
    assert record.binding.bands.pass_min == 0.8
    assert record.binding.bands.needs_review_min == 0.5


def test_question_set_version_is_stable_for_the_same_design():
    first = run_review(
        "# PRD", _design(), "artifact", system_one=lambda request: _passing_answers()
    )
    second = run_review(
        "# PRD", _design(), "artifact", system_one=lambda request: _passing_answers()
    )

    assert first.binding.question_set_version == second.binding.question_set_version


def test_normalize_maps_a_noul_answer_to_a_verdict():
    assert _normalize(NoulAnswer(noul=0.9)) == JevAnswer(0.9)
    assert _normalize(NoulAnswer(noul=0.2)) == JevAnswer(0.2)


def test_normalize_ignores_other_answers():
    assert _normalize(object()) == JevAnswer(None)
