from pydantic import BaseModel


class ReviewStep(BaseModel):
    """One step as the review sees it: the original action and expected result."""

    index: int
    action: str
    expected_result: str


class ReviewCase(BaseModel):
    """One case as the review sees it, with its steps kept separate."""

    index: int
    requirement_ids: list[str]
    module_feature: str
    test_scenario: str
    steps: list[ReviewStep]


class ReviewSubject(BaseModel):
    """The PRD and cases a review judges."""

    prd: str
    cases: list[ReviewCase]
