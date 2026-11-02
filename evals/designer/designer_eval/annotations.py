"""Plan the deterministic CODE annotations attached to eval units."""

from dataclasses import dataclass

from evals.designer.designer_eval.units import EvalUnit, UnitKind, duplicate_groups
from web_test.planning.schema import DesignOutput


@dataclass(frozen=True)
class AnnotationSpec:
    name: str
    span_id: str
    label: str
    score: float
    metadata: dict[str, object]


def code_annotations(units: list[EvalUnit], design: DesignOutput) -> list[AnnotationSpec]:
    duplicate_by_case: dict[str, list[str]] = {}
    for ids in duplicate_groups(design).values():
        for cid in ids:
            duplicate_by_case[cid] = [other for other in ids if other != cid]

    annotations: list[AnnotationSpec] = []
    for unit in units:
        if unit.kind != UnitKind.CLAIM:
            continue
        requirement_id = unit.attributes["claim.requirement_id"]
        cid = unit.attributes["claim.case_id"]
        exists = unit.attributes["claim.requirement_exists"] == "true"
        annotations.append(
            AnnotationSpec(
                name="requirement_exists",
                span_id=unit.span_id,
                label="valid" if exists else "invented",
                score=1.0 if exists else 0.0,
                metadata={
                    "claim_id": unit.target_id,
                    "requirement_id": requirement_id,
                    "case_id": cid,
                },
            )
        )
        duplicates = duplicate_by_case.get(cid, [])
        annotations.append(
            AnnotationSpec(
                name="case_duplicate",
                span_id=unit.span_id,
                label="duplicate" if duplicates else "unique",
                score=0.0 if duplicates else 1.0,
                metadata={
                    "claim_id": unit.target_id,
                    "case_id": cid,
                    "duplicate_with": duplicates,
                },
            )
        )
    return annotations
