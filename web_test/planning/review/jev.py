from collections.abc import Callable, Mapping
from dataclasses import dataclass

from typesafe_sdk import AsyncTypeSafeClient, Noul, NoulAnswer, SystemOneResponse

from web_test._run import run_sync
from web_test.planning.review.subject import ReviewSubject

JEV_MODEL = "jev-1.13.0"


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


def _normalize(answer: object) -> JevAnswer:
    if isinstance(answer, NoulAnswer):
        return JevAnswer(probability=answer.noul)
    return JevAnswer(probability=None)


def typesafe_system_one(request: ReviewRequest) -> dict[str, JevAnswer]:
    """Call TypeSafe's System One (`TYPESAFE_API_KEY`, `TYPESAFE_BASE_URL`)."""

    async def _call() -> SystemOneResponse:
        async with AsyncTypeSafeClient() as client:
            return await client.system_one(
                request.subject.model_dump(), request.questions, model=JEV_MODEL
            )

    response = run_sync(_call())
    return {name: _normalize(answer) for name, answer in response.answers.items()}
