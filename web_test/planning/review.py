from collections.abc import Callable, Mapping
from dataclasses import dataclass

from pydantic import BaseModel
from typesafe_sdk import AsyncTypeSafeClient, Noul, NoulAnswer, SystemOneResponse

from web_test._run import run_sync
from web_test.planning.schema import DesignOutput

JEV_MODEL = "jev-latest"


class ReviewCase(BaseModel):
    """One case as the Jev state sees it: each step flattened to an `action -> expected` line."""

    index: int
    requirement_ids: list[str]
    module_feature: str
    test_scenario: str
    steps: list[str]


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
    # One question per case; the key carries the 1-based index so Jev's name-keyed answers map back
    # to a case (it matches ReviewCase.index, and `_label` recovers the case from the key).
    return {
        f"grounded_{index}": Noul(
            instructions=(
                f"Is case {index} ({case.test_scenario!r}) directly supported by the PRD text, "
                "rather than inferred from behaviour the PRD does not state?"
            )
        )
        for index, case in enumerate(design.cases, start=1)
    }


def build_request(prd_text: str, design: DesignOutput) -> ReviewRequest:
    """The Jev request: the PRD, the designer's cases, and the groundedness questions."""
    state = ReviewState(
        prd=prd_text,
        cases=[
            ReviewCase(
                index=index,
                requirement_ids=case.requirement_ids,
                module_feature=case.module_feature,
                test_scenario=case.test_scenario,
                steps=[f"{step.action} -> {step.expected_result}" for step in case.steps],
            )
            for index, case in enumerate(design.cases, start=1)
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
    request = build_request(prd_text, design)
    try:
        decisions = system_one(request)
    except Exception:  # advisory: no key, network/SDK error, etc. → skip the review rather than fail plan
        return None
    return decisions or None
