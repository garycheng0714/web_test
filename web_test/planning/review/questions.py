import json
from collections.abc import Mapping
from dataclasses import dataclass

from typesafe_sdk import Noul, NoulCriteria

from web_test.planning.review.subject import ReviewCase, ReviewStep, ReviewSubject
from web_test.planning.review.verification import CheckDimension, digest_text

STEP_QUALITY_DIMENSIONS: tuple[CheckDimension, ...] = (
    CheckDimension.STEP_REASONABLE,
    CheckDimension.STEP_COMPLETE,
    CheckDimension.STEP_OBSERVABLE,
)


@dataclass(frozen=True)
class ExpectedCheck:
    question_id: str
    label: str
    dimension: CheckDimension


def ac_id(case_index: int) -> str:
    return f"ac_{case_index}"


def step_key(case_index: int, step_index: int) -> str:
    return f"step_{case_index}_{step_index}"


def step_id(case_index: int, step_index: int, dimension: CheckDimension) -> str:
    return f"{step_key(case_index, step_index)}_{dimension}"


def case_key(case_index: int) -> str:
    return f"case_{case_index}"


def case_label(case: ReviewCase) -> str:
    return f"Case {case.index}: {case.test_scenario}"


def step_label(case: ReviewCase, step: ReviewStep) -> str:
    return f"Case {case.index}, step {step.index}: {step.action}"


def ac_question(case: ReviewCase) -> Noul:
    return Noul(
        instructions=(
            f"Is case {case.index} ({case.test_scenario!r}) directly supported by the PRD "
            "requirement text and acceptance criteria? Judge the scenario, preconditions, "
            "all steps, and all expected results together. A setup step needed to reach an "
            "AC is permitted."
        ),
        criteria=NoulCriteria(
            true=(
                "Every step and expected result is required or permitted by the PRD "
                "requirement text and AC, and no behaviour is invented or contradicted."
            ),
            false=(
                "At least one step or expected result is unsupported by the PRD requirement "
                "text or AC, contradicts it, or invents behaviour."
            ),
        ),
    )


def step_questions(case_index: int, step_index: int) -> dict[str, Noul]:
    """The reasonable, complete, and observable questions for one step."""
    return {
        step_id(case_index, step_index, CheckDimension.STEP_REASONABLE): Noul(
            instructions=(
                f"Does step {step_index} of case {case_index} name a concrete action and "
                "target that exists in the supplied PRD text and is consistent with the PRD "
                "flow?"
            ),
            criteria=NoulCriteria(
                true=(
                    "The action and target are concrete and appear in, or follow directly "
                    "from, the supplied PRD text and PRD flow."
                ),
                false=(
                    "The action or target is absent from the PRD text, contradicts it, or "
                    "skips a necessary part of the flow."
                ),
            ),
        ),
        step_id(case_index, step_index, CheckDimension.STEP_COMPLETE): Noul(
            instructions=(
                f"Does step {step_index} of case {case_index} include every action required "
                "to produce its expected result, including required data entry?"
            ),
            criteria=NoulCriteria(
                true=(
                    "The step includes all required actions and inputs; nothing needed for "
                    "the expected result is missing."
                ),
                false=(
                    "A required action or input is missing, so the step as written cannot "
                    "produce the expected result."
                ),
            ),
        ),
        step_id(case_index, step_index, CheckDimension.STEP_OBSERVABLE): Noul(
            instructions=(
                f"Is the expected result of step {step_index} of case {case_index} a "
                "specific, observable outcome that a manual tester could verify from the "
                "PRD text or its verbatim messages?"
            ),
            criteria=NoulCriteria(
                true=(
                    "The expected result names a specific visible page, field, text, or state "
                    "that the supplied PRD text describes."
                ),
                false=(
                    "The expected result is vague, unstated, or not something the supplied "
                    "PRD text lets a tester observe."
                ),
            ),
        ),
    }


def questions_for_subject(subject: ReviewSubject) -> dict[str, Noul]:
    """Build every Jev question for a review subject."""
    questions: dict[str, Noul] = {}
    for case in subject.cases:
        questions[ac_id(case.index)] = ac_question(case)
        for step in case.steps:
            questions.update(step_questions(case.index, step.index))
    return questions


def question_set_version(questions: Mapping[str, Noul]) -> str:
    payload = {name: question.model_dump() for name, question in sorted(questions.items())}
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return digest_text(encoded)[:16]


def expected_checks(subject: ReviewSubject) -> list[ExpectedCheck]:
    """The question ids, labels, and dimensions that the record aggregates."""
    checks: list[ExpectedCheck] = []
    for case in subject.cases:
        checks.append(
            ExpectedCheck(ac_id(case.index), case_label(case), CheckDimension.AC_ALIGNMENT)
        )
        for step in case.steps:
            for dimension in STEP_QUALITY_DIMENSIONS:
                checks.append(
                    ExpectedCheck(
                        step_id(case.index, step.index, dimension),
                        step_label(case, step),
                        dimension,
                    )
                )
    return checks
