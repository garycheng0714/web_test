import json
from collections.abc import Callable, Mapping

from typesafe_sdk import Noul

from web_test.planning.review.aggregation import aggregate_checks
from web_test.planning.review.jev import (
    JEV_MODEL,
    JevAnswer,
    ReviewRequest,
    SystemOne,
    _typesafe_system_one,
)
from web_test.planning.review.questions import expected_checks, questions_for_subject
from web_test.planning.review.subject import ReviewCase, ReviewStep, ReviewSubject
from web_test.planning.review.verification import (
    Bands,
    CheckOutcome,
    Override,
    VerificationRecord,
    VerificationStatus,
    digest_text,
)
from web_test.planning.schema import DesignOutput

DEFAULT_BANDS = Bands()

# A seam over the whole review: takes the PRD, design, and rendered artifact.
Reviewer = Callable[[str, DesignOutput, str], VerificationRecord]


def _subject_from_design(prd_text: str, design: DesignOutput) -> ReviewSubject:
    return ReviewSubject(
        prd=prd_text,
        cases=[
            ReviewCase(
                index=case_index,
                requirement_ids=case.requirement_ids,
                module_feature=case.module_feature,
                test_scenario=case.test_scenario,
                steps=[
                    ReviewStep(
                        index=step_index,
                        action=step.action,
                        expected_result=step.expected_result,
                    )
                    for step_index, step in enumerate(case.steps, start=1)
                ],
            )
            for case_index, case in enumerate(design.cases, start=1)
        ],
    )


def _question_set_version(questions: Mapping[str, Noul]) -> str:
    payload = {name: question.model_dump() for name, question in sorted(questions.items())}
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return digest_text(encoded)[:16]


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
        status=status,
        checks=tuple(checks),
        steps=tuple(steps),
        cases=tuple(cases),
        prd_digest=digest_text(subject.prd),
        artifact_digest=digest_text(artifact_text),
        model=model,
        question_set_version=question_set_version,
        bands=bands,
        blocked_reason=blocked_reason,
        override=override,
    )


def run_review_on(
    subject: ReviewSubject,
    artifact_text: str = "",
    *,
    system_one: SystemOne = _typesafe_system_one,
    bands: Bands = DEFAULT_BANDS,
) -> VerificationRecord:
    """Judge an existing review subject and always return a record, blocked or not."""
    try:
        questions = questions_for_subject(subject)
        request = ReviewRequest(subject=subject, questions=questions)
        version = _question_set_version(questions)
    except Exception as error:  # noqa: BLE001 - a malformed subject must not fail the plan
        return build_record(
            subject,
            {},
            artifact_text=artifact_text,
            question_set_version="",
            bands=bands,
            blocked_reason=f"request build failed: {error}",
        )

    return _review_request(request, artifact_text, version, system_one=system_one, bands=bands)


def _review_request(
    request: ReviewRequest,
    artifact_text: str,
    version: str,
    *,
    system_one: SystemOne,
    bands: Bands,
) -> VerificationRecord:
    try:
        answers = system_one(request)
    except Exception as error:  # noqa: BLE001 - the record must carry the blocked reason
        return build_record(
            request.subject,
            {},
            artifact_text=artifact_text,
            question_set_version=version,
            bands=bands,
            blocked_reason=f"Jev call failed: {error}",
        )

    if not answers:
        return build_record(
            request.subject,
            {},
            artifact_text=artifact_text,
            question_set_version=version,
            bands=bands,
            blocked_reason="Jev returned no answers",
        )

    return build_record(
        request.subject,
        answers,
        artifact_text=artifact_text,
        question_set_version=version,
        bands=bands,
    )


def run_review(
    prd_text: str,
    design: DesignOutput,
    artifact_text: str = "",
    *,
    system_one: SystemOne = _typesafe_system_one,
    bands: Bands = DEFAULT_BANDS,
) -> VerificationRecord:
    """Ask Jev about a design and return the verification record, or a blocked record when it
    cannot answer."""
    return run_review_on(
        _subject_from_design(prd_text, design),
        artifact_text,
        system_one=system_one,
        bands=bands,
    )
