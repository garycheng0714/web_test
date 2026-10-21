from collections.abc import Mapping

from web_test.planning.review.aggregation import aggregate_checks
from web_test.planning.review.jev import JEV_MODEL, JevAnswer
from web_test.planning.review.questions import expected_checks
from web_test.planning.review.subject import ReviewSubject
from web_test.planning.review.verification import (
    Bands,
    CheckOutcome,
    Override,
    VerificationBinding,
    VerificationRecord,
    VerificationResult,
    VerificationStatus,
    digest_text,
)

DEFAULT_BANDS = Bands()


def _check_outcomes(
    subject: ReviewSubject,
    answers: Mapping[str, JevAnswer],
    bands: Bands,
) -> list[CheckOutcome]:
    """Turn Jev's answers into one outcome per expected check."""
    outcomes = []
    for expected in expected_checks(subject):
        answer = answers.get(expected.question_id)
        probability = answer.probability if answer is not None else None
        outcomes.append(
            CheckOutcome(
                question_id=expected.question_id,
                label=expected.label,
                dimension=expected.dimension,
                probability=probability,
                status=bands.classify(probability),
            )
        )
    return outcomes


def _default_blocked_reason(
    checks: list[CheckOutcome], blocked_reason: str | None
) -> str | None:
    """Give a whole-review failure a readable reason when none was supplied."""
    if blocked_reason is None and (
        not checks or all(check.status is VerificationStatus.BLOCKED for check in checks)
    ):
        return "No answer was returned for any check."
    return blocked_reason


def build_record(
    subject: ReviewSubject,
    answers: Mapping[str, JevAnswer],
    *,
    artifact_text: str,
    question_set_version: str,
    model: str = JEV_MODEL,
    bands: Bands = DEFAULT_BANDS,
    blocked_reason: str | None = None,
    override: Override | None = None,
) -> VerificationRecord:
    """Build the per-check, per-step, per-case, and file status from Jev's answers."""
    checks = _check_outcomes(subject, answers, bands)
    blocked_reason = _default_blocked_reason(checks, blocked_reason)
    steps, cases, status = aggregate_checks(subject, checks)

    if blocked_reason and status is not VerificationStatus.FAIL:
        status = VerificationStatus.BLOCKED

    return VerificationRecord(
        result=VerificationResult(
            status=status,
            checks=tuple(checks),
            steps=tuple(steps),
            cases=tuple(cases),
            blocked_reason=blocked_reason,
            override=override,
        ),
        binding=VerificationBinding(
            prd_digest=digest_text(subject.prd),
            artifact_digest=digest_text(artifact_text),
            model=model,
            question_set_version=question_set_version,
            bands=bands,
        ),
    )


def build_blocked_record(
    subject: ReviewSubject,
    *,
    artifact_text: str,
    question_set_version: str,
    reason: str,
    bands: Bands = DEFAULT_BANDS,
) -> VerificationRecord:
    """Build a record for a review that could not produce answers."""
    return build_record(
        subject,
        {},
        artifact_text=artifact_text,
        question_set_version=question_set_version,
        bands=bands,
        blocked_reason=reason,
    )
