from web_test.planning.review.jev import JEV_MODEL, JevAnswer
from web_test.planning.review.questions import expected_checks
from web_test.planning.review.record import (
    DEFAULT_BANDS,
    _check_outcomes,
    _default_blocked_reason,
    build_record,
)
from web_test.planning.review.subject import ReviewCase, ReviewStep, ReviewSubject
from web_test.planning.review.verification import (
    CheckDimension,
    CheckOutcome,
    Override,
    VerificationStatus,
    digest_text,
)


def _subject() -> ReviewSubject:
    return ReviewSubject(
        prd="# PRD",
        cases=[
            ReviewCase(
                index=1,
                requirement_ids=["FR-1"],
                module_feature="Account",
                test_scenario="A",
                steps=[ReviewStep(index=1, action="Go", expected_result="Page shown")],
            )
        ],
    )


def _answers(subject: ReviewSubject, **overrides: JevAnswer) -> dict[str, JevAnswer]:
    return {
        expected.question_id: overrides.get(expected.question_id, JevAnswer(0.95))
        for expected in expected_checks(subject)
    }


def _outcome(status: VerificationStatus) -> CheckOutcome:
    return CheckOutcome(
        question_id="q",
        label="Q",
        dimension=CheckDimension.STEP_CONTINUITY,
        probability=None,
        status=status,
    )


def test_check_outcomes_classifies_answers_and_marks_missing_ones_blocked():
    subject = _subject()

    outcomes = _check_outcomes(
        subject,
        _answers(
            subject,
            ac_1=JevAnswer(0.6),
            step_1_1_continuity=JevAnswer(0.1),
        ),
        DEFAULT_BANDS,
    )
    by_id = {outcome.question_id: outcome for outcome in outcomes}

    assert by_id["ac_1"].status is VerificationStatus.NEEDS_REVIEW
    assert by_id["ac_1"].probability == 0.6
    assert by_id["step_1_1_continuity"].status is VerificationStatus.FAIL
    assert by_id["step_1_1_reasonable"].status is VerificationStatus.PASS

    missing = _check_outcomes(subject, {}, DEFAULT_BANDS)

    assert all(outcome.status is VerificationStatus.BLOCKED for outcome in missing)
    assert all(outcome.probability is None for outcome in missing)


def test_default_blocked_reason_keeps_explicit_and_fills_whole_review_failures():
    assert _default_blocked_reason([_outcome(VerificationStatus.BLOCKED)], "explicit") == "explicit"
    assert (
        _default_blocked_reason([_outcome(VerificationStatus.BLOCKED)], None)
        == "No answer was returned for any check."
    )
    assert (
        _default_blocked_reason([], None)
        == "No answer was returned for any check."
    )
    assert (
        _default_blocked_reason(
            [_outcome(VerificationStatus.PASS), _outcome(VerificationStatus.BLOCKED)],
            None,
        )
        is None
    )


def test_build_record_binds_metadata_and_carries_override():
    subject = _subject()
    override = Override(
        original=VerificationStatus.NEEDS_REVIEW,
        reason="Expected result is observable in the PRD.",
        head_sha="abc123",
    )

    record = build_record(
        subject,
        _answers(subject),
        test_case_text="# artifact\n",
        question_set_version="qsv",
        override=override,
    )

    assert record.result.status is VerificationStatus.PASS
    assert record.binding.prd_digest == digest_text(subject.prd)
    assert record.binding.test_case_digest == digest_text("# artifact\n")
    assert record.binding.model == JEV_MODEL
    assert record.binding.question_set_version == "qsv"
    assert record.binding.bands == DEFAULT_BANDS
    assert record.result.override == override


def test_fail_wins_over_blocked_reason():
    subject = _subject()

    record = build_record(
        subject,
        _answers(subject, ac_1=JevAnswer(0.1)),
        test_case_text="",
        question_set_version="qsv",
        blocked_reason="Jev call failed",
    )

    assert record.result.status is VerificationStatus.FAIL
    assert record.result.blocked_reason == "Jev call failed"
