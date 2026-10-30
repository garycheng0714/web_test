from unittest.mock import MagicMock

from typesafe_sdk import Noul

import web_test.planning.review.service as review_module
from review_helpers import (
    answers_for,
    make_case,
    make_design,
    passing_system_one,
    render_case,
)
from web_test.planning.review import (
    JEV_MODEL,
    JevAnswer,
    ReviewRequest,
    ReviewStep,
    run_review,
)
from web_test.planning.review.questions import STEP_QUALITY_DIMENSIONS
from web_test.planning.review.verification import VerificationStatus, digest_text
from web_test.planning.schema import DesignOutput


def _question_ids() -> list[str]:
    ids = [f"ac_{index}" for index in range(1, 4)]
    ids += [
        f"step_{case_index}_1_{check}"
        for case_index in range(1, 4)
        for check in STEP_QUALITY_DIMENSIONS
    ]
    return ids


def test_run_review_builds_the_three_checks():
    captured = {}

    def system_one(request):
        captured["request"] = request
        return passing_system_one(request)

    run_review("# PRD", make_design(), "artifact", system_one=system_one)
    request = captured["request"]

    assert isinstance(request, ReviewRequest)
    assert set(request.questions) == set(_question_ids())
    assert request.subject.prd == "# PRD"
    assert request.subject.cases[0].index == 1
    assert request.subject.cases[0].steps == [
        ReviewStep(index=1, action="Go", expected_result="Page shown")
    ]
    assert isinstance(request.questions["ac_1"], Noul)


def test_run_review_passes_case_preconditions_into_the_subject():
    captured = {}

    def system_one(request):
        captured["request"] = request
        return passing_system_one(request)

    case = make_case(preconditions=["User is on /login"])
    run_review("# PRD", DesignOutput(cases=[case]), "artifact", system_one=system_one)

    assert captured["request"].subject.cases[0].preconditions == ["User is on /login"]


def test_run_review_aggregates_step_case_and_file_verdicts():
    record = run_review(
        "# PRD",
        make_design(),
        "artifact",
        system_one=lambda request: answers_for(
            request,
            ac_2=JevAnswer(0.05),
            step_3_1_continuity=JevAnswer(0.6),
        ),
    )

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
        make_design(),
        "artifact",
        system_one=lambda request: {"ac_1": JevAnswer(0.95)},
    )

    assert record.result.status is VerificationStatus.BLOCKED
    assert record.result.cases[0].status is VerificationStatus.BLOCKED
    assert any(check.status is VerificationStatus.BLOCKED for check in record.result.checks)


def test_blocked_dominates_needs_review():
    def system_one(request):
        answers = answers_for(request, step_1_1_continuity=JevAnswer(0.6))
        answers.pop("step_1_1_observable")
        return answers

    record = run_review("# PRD", make_design(), "artifact", system_one=system_one)

    assert record.result.steps[0].status is VerificationStatus.BLOCKED
    assert record.result.cases[0].status is VerificationStatus.BLOCKED
    assert record.result.status is VerificationStatus.BLOCKED


def test_fail_dominates_blocked():
    record = run_review(
        "# PRD",
        make_design(),
        "artifact",
        system_one=lambda request: answers_for(request, ac_1=JevAnswer(0.05)),
    )

    assert record.result.cases[0].status is VerificationStatus.FAIL
    assert record.result.status is VerificationStatus.FAIL


def test_unknown_answers_only_are_blocked_with_a_reason():
    record = run_review(
        "# PRD",
        make_design(),
        "artifact",
        system_one=lambda request: {"surprise": JevAnswer(0.95)},
    )

    assert record.result.status is VerificationStatus.BLOCKED
    assert record.result.blocked_reason == "No answer was returned for any check."


def test_question_set_version_failure_is_blocked(monkeypatch):
    def _boom(questions):
        raise ValueError("bad question set")

    monkeypatch.setattr(review_module, "question_set_version", _boom)

    record = run_review("# PRD", make_design(), "artifact", system_one=passing_system_one)

    assert record.result.status is VerificationStatus.BLOCKED
    assert "request build failed" in (record.result.blocked_reason or "")


def test_run_review_returns_blocked_when_the_call_fails():
    record = run_review(
        "# PRD",
        make_design(),
        "artifact",
        system_one=MagicMock(side_effect=RuntimeError("no key")),
    )

    assert record.result.status is VerificationStatus.BLOCKED
    assert "Jev call failed" in (record.result.blocked_reason or "")
    assert all(check.status is VerificationStatus.BLOCKED for check in record.result.checks)


def test_run_review_returns_blocked_on_empty_answers():
    record = run_review("# PRD", make_design(), "artifact", system_one=lambda request: {})

    assert record.result.status is VerificationStatus.BLOCKED
    assert record.result.blocked_reason == "Jev returned no answers"


def test_record_binds_digests_model_and_question_set():
    record = run_review(
        "# PRD",
        make_design(),
        "artifact",
        system_one=passing_system_one,
    )

    assert record.binding.prd_digest == digest_text("# PRD")
    assert record.binding.test_case_digest == digest_text("artifact")
    assert record.binding.model == JEV_MODEL
    assert record.binding.question_set_version
    assert record.binding.bands.pass_min == 0.8
    assert record.binding.bands.needs_review_min == 0.5


def test_question_set_version_is_stable_for_the_same_design():
    first = run_review("# PRD", make_design(), "artifact", system_one=passing_system_one)
    second = run_review("# PRD", make_design(), "artifact", system_one=passing_system_one)

    assert first.binding.question_set_version == second.binding.question_set_version


def test_run_review_combines_a_structure_failure_with_jev() -> None:
    case = make_case(steps=[{"action": "Go", "expected_result": ""}])
    artifact = render_case(case)

    record = run_review(
        "# PRD",
        DesignOutput(cases=[case]),
        artifact,
        system_one=passing_system_one,
    )

    assert record.result.jev_status is VerificationStatus.PASS
    assert record.result.status is VerificationStatus.FAIL
    assert any(
        outcome.check_id == "step_1_1_expected" and outcome.status is VerificationStatus.FAIL
        for outcome in record.result.structure
    )
