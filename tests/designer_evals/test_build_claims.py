import pytest

from evals.designer import build_claims
from evals.designer.designer_eval.artifacts import RunSummary
from evals.designer.designer_eval.labels import AnnotationRow
from evals.designer.designer_eval.units import EvalUnit, UnitKind

RUN = RunSummary(
    run_id="run-1",
    prd="prd.md",
    prd_path="prd/prd.md",
    model="model-1",
    project="project-1",
    created_at="2026-11-13T00:00:00Z",
    requirements=1,
    cases=1,
    claims=1,
    units=1,
    annotations=0,
    usage={},
)


def _claim(claim_id: str, span_id: str, requirement_id: str = "FR-ACC-01") -> EvalUnit:
    return EvalUnit(
        kind=UnitKind.CLAIM,
        target_id=claim_id,
        span_id=span_id,
        name=f"claim {claim_id}",
        attributes={
            "claim.requirement_id": requirement_id,
            "claim.case_id": claim_id.split("->")[0],
            "output.value": f"## Case: {claim_id}",
        },
    )


def _requirement(span_id: str) -> EvalUnit:
    return EvalUnit(
        kind=UnitKind.REQUIREMENT,
        target_id="FR-ACC-01",
        span_id=span_id,
        name="requirement FR-ACC-01",
        attributes={},
    )


def _label(
    span_id: str,
    name: str,
    label: str | None = None,
    explanation: str | None = None,
    *,
    kind: str = "HUMAN",
):
    return AnnotationRow(
        run_id="run-1",
        prd="prd.md",
        target_kind="claim",
        target_id="case-1->FR-ACC-01",
        span_id=span_id,
        annotation=name,
        annotator_kind=kind,
        annotator="local" if kind == "HUMAN" else "code",
        label=label,
        explanation=explanation,
    )


def test_build_rows_joins_claim_units_with_human_labels():
    units = [_requirement("req-1"), _claim("case-1->FR-ACC-01", "span-1")]
    labels = [
        _label("span-1", "claim_alignment", "pass"),
        _label("req-1", "claim_alignment", "pass"),
        _label("span-1", "case_duplicate", kind="CODE"),
    ]

    rows = build_claims.build_rows(units, labels, RUN)

    assert len(rows) == 1
    row = rows[0]
    assert row.claim_id == "case-1->FR-ACC-01"
    assert row.source_run == "run-1"
    assert row.requirement_id == "FR-ACC-01"
    assert row.case_markdown == "## Case: case-1->FR-ACC-01"
    assert (row.human_label, row.human_mode, row.human_reason) == ("pass", None, None)


def test_build_rows_keeps_the_mode_and_reason_of_a_failure():
    units = [_claim("case-1->FR-ACC-01", "span-1")]
    labels = [
        _label("span-1", "claim_alignment", "fail"),
        _label("span-1", "claim_failure_mode", "wrong_actions"),
        _label("span-1", "claim_reason", explanation="the steps sign up instead of logging in"),
    ]

    row = build_claims.build_rows(units, labels, RUN)[0]

    assert row.human_mode == "wrong_actions"
    assert row.human_reason == "the steps sign up instead of logging in"


def test_build_rows_drops_a_mode_left_on_a_passing_claim():
    units = [_claim("case-1->FR-ACC-01", "span-1")]
    labels = [
        _label("span-1", "claim_alignment", "pass"),
        _label("span-1", "claim_failure_mode", "duplicated"),
    ]

    assert build_claims.build_rows(units, labels, RUN)[0].human_mode is None


def test_build_rows_rejects_a_claim_without_an_alignment():
    units = [_claim("case-1->FR-ACC-01", "span-1"), _claim("case-2->FR-ACC-01", "span-2")]
    labels = [_label("span-1", "claim_alignment", "pass")]

    with pytest.raises(ValueError, match="case-2->FR-ACC-01"):
        build_claims.build_rows(units, labels, RUN)


def test_build_rows_rejects_an_unknown_alignment():
    units = [_claim("case-1->FR-ACC-01", "span-1")]
    labels = [_label("span-1", "claim_alignment", "maybe")]

    with pytest.raises(ValueError, match="maybe"):
        build_claims.build_rows(units, labels, RUN)


def test_build_rows_rejects_a_failure_without_a_mode():
    units = [_claim("case-1->FR-ACC-01", "span-1")]
    labels = [
        _label("span-1", "claim_alignment", "fail"),
        _label("span-1", "claim_failure_mode", "N/A"),
    ]

    with pytest.raises(ValueError, match="case-1->FR-ACC-01"):
        build_claims.build_rows(units, labels, RUN)
