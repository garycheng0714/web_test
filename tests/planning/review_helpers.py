from collections.abc import Iterable

from web_test.planning.cases_writer import render_document
from web_test.planning.review import JevAnswer
from web_test.planning.review.questions import expected_checks
from web_test.planning.review.subject import ReviewCase, ReviewStep, ReviewSubject
from web_test.planning.schema import Case, DesignOutput

DEFAULT_BASE_URL = "https://example.com"


def make_case(**overrides) -> Case:
    data = {
        "requirement_ids": ["FR-ACC-01"],
        "module_feature": "Account",
        "test_scenario": "Register",
        "steps": [{"action": "Go", "expected_result": "Page shown"}],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        **overrides,
    }
    return Case.model_validate(data)


def make_design(*scenarios: str) -> DesignOutput:
    names = scenarios or ("A", "B", "C")
    return DesignOutput(cases=[make_case(test_scenario=name) for name in names])


def render_case(
    case: Case,
    *,
    id: str = "demo",
    base_url: str = DEFAULT_BASE_URL,
    title: str = "Demo",
    open_questions: Iterable[str] = (),
) -> str:
    return render_document(
        [case],
        id=id,
        base_url=base_url,
        title=title,
        open_questions=open_questions,
    )


def review_case(
    *,
    index: int = 1,
    scenario: str = "A",
    steps: list[ReviewStep] | None = None,
    requirement_ids: list[str] | None = None,
    module_feature: str = "Account",
    preconditions: list[str] | None = None,
) -> ReviewCase:
    return ReviewCase(
        index=index,
        requirement_ids=requirement_ids
        if requirement_ids is not None
        else ["FR-1"],
        module_feature=module_feature,
        test_scenario=scenario,
        preconditions=preconditions if preconditions is not None else [],
        steps=steps
        if steps is not None
        else [
            ReviewStep(index=1, action="Go", expected_result="Page shown"),
            ReviewStep(index=2, action="Submit", expected_result="Done"),
        ],
    )


def review_subject(cases: list[ReviewCase] | None = None) -> ReviewSubject:
    return ReviewSubject(
        prd="# PRD",
        cases=cases if cases is not None else [review_case()],
    )


def answers_for(request, **overrides: JevAnswer) -> dict[str, JevAnswer]:
    return {
        question_id: overrides.get(question_id, JevAnswer(0.95))
        for question_id in request.questions
    }


def answers_for_subject(
    subject: ReviewSubject, **overrides: JevAnswer
) -> dict[str, JevAnswer]:
    return {
        check.question_id: overrides.get(check.question_id, JevAnswer(0.95))
        for check in expected_checks(subject)
    }


def passing_system_one(request) -> dict[str, JevAnswer]:
    return {question_id: JevAnswer(0.95) for question_id in request.questions}
