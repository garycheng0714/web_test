from web_test.planning.review.aggregation import aggregate_checks
from web_test.planning.review.questions import expected_checks
from web_test.planning.review.subject import ReviewCase, ReviewStep, ReviewSubject
from web_test.planning.review.verification import CheckOutcome, VerificationStatus

_PROBABILITY = {
    VerificationStatus.PASS: 0.95,
    VerificationStatus.NEEDS_REVIEW: 0.6,
    VerificationStatus.FAIL: 0.1,
    VerificationStatus.BLOCKED: None,
}


def _case(
    *,
    index: int = 1,
    scenario: str = "A",
    steps: list[ReviewStep] | None = None,
) -> ReviewCase:
    return ReviewCase(
        index=index,
        requirement_ids=["FR-1"],
        module_feature="Account",
        test_scenario=scenario,
        steps=steps
        or [
            ReviewStep(index=1, action="Go", expected_result="Page shown"),
            ReviewStep(index=2, action="Submit", expected_result="Done"),
        ],
    )


def _subject() -> ReviewSubject:
    return ReviewSubject(prd="# PRD", cases=[_case()])


def _checks(subject: ReviewSubject, **overrides: VerificationStatus) -> list[CheckOutcome]:
    checks = []
    for expected in expected_checks(subject):
        status = overrides.get(expected.question_id, VerificationStatus.PASS)
        checks.append(
            CheckOutcome(
                question_id=expected.question_id,
                label=expected.label,
                dimension=expected.dimension,
                probability=_PROBABILITY[status],
                status=status,
            )
        )
    return checks


def test_all_pass():
    subject = _subject()

    steps, cases, status = aggregate_checks(subject, _checks(subject))

    assert [step.status for step in steps] == [VerificationStatus.PASS] * 2
    assert [case.status for case in cases] == [VerificationStatus.PASS]
    assert status is VerificationStatus.PASS
    assert steps[0].key == "step_1_1"
    assert cases[0].key == "case_1"


def test_step_failure_propagates_to_case_and_file():
    subject = _subject()

    steps, cases, status = aggregate_checks(
        subject, _checks(subject, step_1_1_continuity=VerificationStatus.FAIL)
    )

    assert steps[0].status is VerificationStatus.FAIL
    assert cases[0].status is VerificationStatus.FAIL
    assert status is VerificationStatus.FAIL


def test_precedence_is_fail_over_blocked_over_needs_review():
    subject = _subject()

    steps, cases, status = aggregate_checks(
        subject,
        _checks(
            subject,
            step_1_1_reasonable=VerificationStatus.NEEDS_REVIEW,
            step_1_1_continuity=VerificationStatus.BLOCKED,
            step_1_2_reasonable=VerificationStatus.FAIL,
        ),
    )

    assert steps[0].status is VerificationStatus.BLOCKED
    assert steps[1].status is VerificationStatus.FAIL
    assert cases[0].status is VerificationStatus.FAIL
    assert status is VerificationStatus.FAIL


def test_ac_failure_marks_case_fail_even_when_steps_pass():
    subject = _subject()

    steps, cases, status = aggregate_checks(
        subject, _checks(subject, ac_1=VerificationStatus.FAIL)
    )

    assert [step.status for step in steps] == [VerificationStatus.PASS] * 2
    assert cases[0].status is VerificationStatus.FAIL
    assert status is VerificationStatus.FAIL


def test_file_status_is_the_worst_case():
    subject = ReviewSubject(
        prd="# PRD",
        cases=[
            _case(
                index=1,
                steps=[ReviewStep(index=1, action="Go", expected_result="Page shown")],
            ),
            _case(
                index=2,
                scenario="B",
                steps=[ReviewStep(index=1, action="Go", expected_result="Page shown")],
            ),
        ],
    )

    steps, cases, status = aggregate_checks(
        subject, _checks(subject, step_2_1_continuity=VerificationStatus.NEEDS_REVIEW)
    )

    assert [case.status for case in cases] == [
        VerificationStatus.PASS,
        VerificationStatus.NEEDS_REVIEW,
    ]
    assert status is VerificationStatus.NEEDS_REVIEW


def test_empty_subject_is_blocked():
    steps, cases, status = aggregate_checks(ReviewSubject(prd="", cases=[]), [])

    assert steps == []
    assert cases == []
    assert status is VerificationStatus.BLOCKED
