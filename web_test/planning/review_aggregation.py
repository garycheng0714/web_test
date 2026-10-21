from collections.abc import Mapping

from web_test.planning.review_questions import (
    STEP_QUALITY_DIMENSIONS,
    ac_id,
    case_key,
    case_label,
    step_id,
    step_key,
    step_label,
)
from web_test.planning.review_subject import ReviewSubject
from web_test.planning.verification import (
    CheckOutcome,
    UnitOutcome,
    VerificationStatus,
    worst,
)


def aggregate_checks(
    subject: ReviewSubject,
    checks: list[CheckOutcome],
) -> tuple[list[UnitOutcome], list[UnitOutcome], VerificationStatus]:
    """Roll checks up to steps, cases, and the file status."""
    by_id = {check.question_id: check for check in checks}
    steps = _step_outcomes(subject, by_id)
    cases = _case_outcomes(subject, by_id, steps)
    return steps, cases, worst(case.status for case in cases)


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
