import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from typesafe_sdk import AsyncTypeSafeClient, Noul, NoulAnswer, SystemOneResponse

from web_test._run import run_sync
from web_test.planning.review_questions import (
    STEP_QUALITY_DIMENSIONS,
    ac_id,
    case_key,
    case_label,
    expected_checks,
    questions_for_subject,
    step_id,
    step_key,
    step_label,
)
from web_test.planning.review_subject import ReviewCase, ReviewStep, ReviewSubject
from web_test.planning.schema import DesignOutput
from web_test.planning.verification import (
    Bands,
    CheckOutcome,
    Override,
    UnitOutcome,
    VerificationRecord,
    VerificationStatus,
    digest_text,
    worst,
)

JEV_MODEL = "jev-1.13.0"
DEFAULT_BANDS = Bands()


@dataclass(frozen=True)
class ReviewRequest:
    """The Jev request: the subject to judge and the typed questions about it."""

    subject: ReviewSubject
    questions: Mapping[str, Noul]


@dataclass(frozen=True)
class JevAnswer:
    """One answered question: Jev's probability of yes, or `None` when it did not answer."""

    probability: float | None


# A seam over the Jev call: takes the request, returns an answer per question id.
SystemOne = Callable[[ReviewRequest], dict[str, JevAnswer]]
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


def _step_outcomes(
    subject: ReviewSubject,
    by_id: Mapping[str, CheckOutcome],
) -> list[UnitOutcome]:
    steps = []
    for case in subject.cases:
        for step in case.steps:
            statuses = [
                by_id[step_id(case.index, step.index, dimension)].status
                for dimension in STEP_QUALITY_DIMENSIONS
            ]
            steps.append(
                UnitOutcome(
                    key=step_key(case.index, step.index),
                    label=step_label(case, step),
                    status=worst(statuses),
                )
            )
    return steps


def _case_outcomes(
    subject: ReviewSubject,
    by_id: Mapping[str, CheckOutcome],
    steps: list[UnitOutcome],
) -> list[UnitOutcome]:
    step_status_by_key = {step.key: step.status for step in steps}
    cases = []
    for case in subject.cases:
        ac_status = by_id[ac_id(case.index)].status
        step_statuses = [
            step_status_by_key[step_key(case.index, step.index)] for step in case.steps
        ]
        cases.append(
            UnitOutcome(
                key=case_key(case.index),
                label=case_label(case),
                status=worst([ac_status, *step_statuses]),
            )
        )
    return cases


def _aggregate(
    subject: ReviewSubject,
    checks: list[CheckOutcome],
) -> tuple[list[UnitOutcome], list[UnitOutcome], VerificationStatus]:
    """Roll checks up to steps, cases, and the file status."""
    by_id = {check.question_id: check for check in checks}
    steps = _step_outcomes(subject, by_id)
    cases = _case_outcomes(subject, by_id, steps)
    return steps, cases, worst(case.status for case in cases)


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
    steps, cases, status = _aggregate(subject, checks)

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


def _normalize(answer: object) -> JevAnswer:
    if isinstance(answer, NoulAnswer):
        return JevAnswer(probability=answer.noul)
    return JevAnswer(probability=None)


def _typesafe_system_one(request: ReviewRequest) -> dict[str, JevAnswer]:
    """Call TypeSafe's System One with the built request (reads `TYPESAFE_API_KEY`/`TYPESAFE_BASE_URL`)."""

    async def _call() -> SystemOneResponse:
        async with AsyncTypeSafeClient() as client:
            return await client.system_one(request.subject.model_dump(), request.questions, model=JEV_MODEL)

    response = run_sync(_call())
    return {name: _normalize(answer) for name, answer in response.answers.items()}


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
