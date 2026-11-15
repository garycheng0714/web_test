"""The judged record and the metrics computed from it.

A leaf: the judging call and the report both depend on these types, and they depend on nothing else
in the eval.
"""

from dataclasses import dataclass

from pydantic import BaseModel


class JudgeRecord(BaseModel):
    """One judged claim: the verdict, its audit trail, and the human label it is compared with."""

    claim_id: str
    source_run: str
    requirement_id: str
    case_id: str
    verdict: str
    critique: str
    checks: list[dict[str, object]]
    human_label: str
    human_mode: str | None
    model: str
    prompt_sha256: str


@dataclass(frozen=True)
class JudgeMetrics:
    """Confusion counts live beside the rates so a reader can check the denominators.

    Both rates name their positive class, because `TPR`/`TNR` are read in opposite directions by
    `validate-evaluator` (positive = pass) and by failure detection (positive = fail).
    """

    total: int
    human_fail: int
    human_pass: int
    judged_fail: int
    judged_pass: int
    caught: int
    missed: int
    false_alarm: int
    agreed_pass: int
    fail_recall: float | None
    pass_specificity: float | None
    fail_recall_ci: tuple[float, float] | None
    pass_specificity_ci: tuple[float, float] | None
    disagreements: list[JudgeRecord]
