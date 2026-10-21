from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from web_test.planning.review.verification import CheckDimension


class EvalStep(BaseModel):
    action: str
    expected_result: str


class EvalCase(BaseModel):
    id: str
    label: Literal["good", "bad"]
    tests: str | None = None
    requirement_ids: list[str]
    scenario: str
    preconditions: list[str] = []
    steps: list[EvalStep]


class ExpectedFailure(BaseModel):
    case: str
    dimension: CheckDimension
    step: int | None = None


class KillCriteria(BaseModel):
    caught_min: int = 0
    hard_fail_min: int = 0
    good_false_flags_max: int = 0
    bad_blocked_max: int = 0
    require_each_dimension: bool = True


class EvalSet(BaseModel):
    prd: str
    cases: list[EvalCase]
    expected_failures: list[ExpectedFailure]
    kill_criteria: KillCriteria


def load_eval_set(path: str | Path) -> EvalSet:
    return EvalSet.model_validate_json(Path(path).read_text(encoding="utf-8"))
