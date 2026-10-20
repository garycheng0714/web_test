from collections.abc import Callable, Mapping
from dataclasses import dataclass

from pydantic import BaseModel
from typesafe_sdk import AsyncTypeSafeClient, Noul, NoulAnswer, SystemOneResponse

from web_test._run import run_sync
from web_test.planning.schema import DesignOutput

JEV_MODEL = "jev-1.13.0"


class ReviewStep(BaseModel):
    """One step as the Jev state sees it: the original action and expected result."""

    index: int
    action: str
    expected_result: str


class ReviewCase(BaseModel):
    """One case as the Jev state sees it, with its steps kept separate."""

    index: int
    requirement_ids: list[str]
    module_feature: str
    test_scenario: str
    steps: list[ReviewStep]


class ReviewState(BaseModel):
    """The material Jev judges: the PRD and the designer's cases."""

    prd: str
    cases: list[ReviewCase]


@dataclass(frozen=True)
class ReviewRequest:
    """The Jev request: the state to judge and the typed questions about it."""

    state: ReviewState
    questions: Mapping[str, Noul]


@dataclass(frozen=True)
class Verdict:
    """One answered question: the value and Jev's probability of yes."""

    value: bool | None
    probability: float | None


# A seam over the Jev call: takes the request, returns a verdict per question id.
SystemOne = Callable[[ReviewRequest], dict[str, Verdict]]
# A seam over the whole review: takes the PRD + design, returns a verdict per question id (or `None`).
Reviewer = Callable[[str, DesignOutput], dict[str, Verdict] | None]


def _questions(design: DesignOutput) -> dict[str, Noul]:
    """The three checks: AC alignment, step quality, and expected-result observability."""
    questions: dict[str, Noul] = {}

    for case_index, case in enumerate(design.cases, start=1):
        questions[f"ac_{case_index}"] = Noul(
            instructions=(
                f"Is case {case_index} ({case.test_scenario!r}) directly supported by the PRD "
                "requirement text and acceptance criteria? Judge the scenario, preconditions, "
                "all steps, and all expected results together. A setup step needed to reach an "
                "AC is permitted."
            ),
            criteria={
                "true": (
                    "Every step and expected result is required or permitted by the PRD "
                    "requirement text and AC, and no behaviour is invented or contradicted."
                ),
                "false": (
                    "At least one step or expected result is unsupported by the PRD requirement "
                    "text or AC, contradicts it, or invents behaviour."
                ),
            },
        )

        for step_index, _ in enumerate(case.steps, start=1):
            questions[f"step_{case_index}_{step_index}_reasonable"] = Noul(
                instructions=(
                    f"Does step {step_index} of case {case_index} name a concrete action and "
                    "target that exists in the supplied PRD text and is consistent with the PRD "
                    "flow?"
                ),
                criteria={
                    "true": (
                        "The action and target are concrete and appear in, or follow directly "
                        "from, the supplied PRD text and PRD flow."
                    ),
                    "false": (
                        "The action or target is absent from the PRD text, contradicts it, or "
                        "skips a necessary part of the flow."
                    ),
                },
            )
            questions[f"step_{case_index}_{step_index}_complete"] = Noul(
                instructions=(
                    f"Does step {step_index} of case {case_index} include every action required "
                    "to produce its expected result, including required data entry?"
                ),
                criteria={
                    "true": (
                        "The step includes all required actions and inputs; nothing needed for "
                        "the expected result is missing."
                    ),
                    "false": (
                        "A required action or input is missing, so the step as written cannot "
                        "produce the expected result."
                    ),
                },
            )
            questions[f"step_{case_index}_{step_index}_observable"] = Noul(
                instructions=(
                    f"Is the expected result of step {step_index} of case {case_index} a "
                    "specific, observable outcome that a manual tester could verify from the "
                    "PRD text or its verbatim messages?"
                ),
                criteria={
                    "true": (
                        "The expected result names a specific visible page, field, text, or state "
                        "that the supplied PRD text describes."
                    ),
                    "false": (
                        "The expected result is vague, unstated, or not something the supplied "
                        "PRD text lets a tester observe."
                    ),
                },
            )

    return questions


def build_request(prd_text: str, design: DesignOutput) -> ReviewRequest:
    """The Jev request: the PRD, the designer's cases, and the three quality checks."""
    state = ReviewState(
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
    return ReviewRequest(state=state, questions=_questions(design))


def _normalize(answer: object) -> Verdict:
    if isinstance(answer, NoulAnswer):
        return Verdict(value=answer.noul >= 0.5, probability=answer.noul)
    return Verdict(value=None, probability=None)


def _typesafe_system_one(request: ReviewRequest) -> dict[str, Verdict]:
    """Call TypeSafe's System One with the built request (reads `TYPESAFE_API_KEY`/`TYPESAFE_BASE_URL`)."""

    async def _call() -> SystemOneResponse:
        async with AsyncTypeSafeClient() as client:
            return await client.system_one(request.state.model_dump(), request.questions, model=JEV_MODEL)

    response = run_sync(_call())
    return {name: _normalize(answer) for name, answer in response.answers.items()}


def run_review(
    prd_text: str,
    design: DesignOutput,
    *,
    system_one: SystemOne = _typesafe_system_one,
) -> dict[str, Verdict] | None:
    """Ask Jev for a verdict per question; `None` when the review is unavailable."""
    try:
        request = build_request(prd_text, design)
        decisions = system_one(request)
    except Exception:  # advisory: no key, network/SDK error, etc. → skip the review rather than fail plan
        return None
    return decisions or None
