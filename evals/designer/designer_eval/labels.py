"""Read and write `labels.jsonl`: the Phoenix annotations exported for one eval run."""

from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from evals.designer.designer_eval.jsonl import read_rows
from evals.designer.designer_eval.units import UnitKind


class AnnotationRow(BaseModel):
    """One exported annotation. Boundary data, so the Phoenix API decides what a row may hold."""

    run_id: str
    prd: str
    target_kind: UnitKind
    target_id: str
    span_id: str
    annotation: str
    annotator_kind: Literal["HUMAN", "CODE"]
    annotator: str
    label: str | None = None
    score: float | None = None
    explanation: str | None = None
    identifier: str = ""
    annotation_id: str | None = None
    source: str | None = None
    metadata: dict[str, object] = {}


def read_labels(path: Path) -> list[AnnotationRow]:
    return read_rows(path, AnnotationRow)


def human_fields(
    rows: Iterable[AnnotationRow], *, by: Literal["span_id", "target_id"]
) -> dict[str, dict[str, AnnotationRow]]:
    """Group the HUMAN rows by one id, so a caller can read `fields["claim_alignment"].label`."""
    fields: dict[str, dict[str, AnnotationRow]] = {}
    for row in rows:
        if row.annotator_kind != "HUMAN":
            continue
        key = row.span_id if by == "span_id" else row.target_id
        fields.setdefault(key, {})[row.annotation] = row
    return fields
