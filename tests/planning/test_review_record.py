from review_helpers import answers_for_subject, review_subject
from web_test.planning.review.jev import JEV_MODEL, JevAnswer
from web_test.planning.review.record import (
    DEFAULT_BANDS,
    _check_outcomes,
    _default_blocked_reason,
    build_blocked_record,
    build_record,
)
from web_test.planning.review.structure import CHECK_SET_VERSION
from web_test.planning.review.verification import (
    CheckDimension,
    CheckOutcome,
    DeterministicOutcome,
    Override,
    VerificationStatus,
    digest_text,
)


def _outcome(status: VerificationStatus) -> CheckOutcome:
    return CheckOutcome(
        question_id="q",
        label="Q",
        dimension=CheckDimension.STEP_CONTINUITY,
        probability=None,
        status=status,
    )


def test_check_outcomes_classifies_answers_and_marks_missing_ones_blocked():
    subject = review_subject()

    outcomes = _check_outcomes(
        subject,
        answers_for_subject(
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
    subject = review_subject()
    override = Override(
        original=VerificationStatus.NEEDS_REVIEW,
        reason="Expected result is observable in the PRD.",
        head_sha="abc123",
    )

    record = build_record(
        subject,
        answers_for_subject(subject),
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
    assert record.binding.check_set_version == CHECK_SET_VERSION
    assert record.result.override == override


def test_fail_wins_over_blocked_reason():
    subject = review_subject()

    record = build_record(
        subject,
        answers_for_subject(subject, ac_1=JevAnswer(0.1)),
        test_case_text="",
        question_set_version="qsv",
        blocked_reason="Jev call failed",
    )

    assert record.result.status is VerificationStatus.FAIL
    assert record.result.blocked_reason == "Jev call failed"


def _structure_failure() -> tuple[DeterministicOutcome, ...]:
    return (
        DeterministicOutcome(
            "front_matter",
            "Front matter is present and valid",
            VerificationStatus.FAIL,
            "front matter is missing or invalid",
        ),
    )


def test_structure_failure_wins_over_a_jev_pass():
    subject = review_subject()

    record = build_record(
        subject,
        answers_for_subject(subject),
        test_case_text="# artifact\n",
        question_set_version="qsv",
        structure=_structure_failure(),
    )

    assert record.result.jev_status is VerificationStatus.PASS
    assert record.result.status is VerificationStatus.FAIL
    assert record.result.structure == _structure_failure()


def test_structure_failure_is_not_masked_by_a_blocked_jev():
    subject = review_subject()

    record = build_blocked_record(
        subject,
        test_case_text="",
        question_set_version="",
        reason="Jev unavailable",
        structure=_structure_failure(),
    )

    assert record.result.jev_status is VerificationStatus.BLOCKED
    assert record.result.status is VerificationStatus.FAIL
    assert record.result.blocked_reason == "Jev unavailable"
