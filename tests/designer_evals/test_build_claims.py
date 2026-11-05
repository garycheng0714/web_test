import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]


def _load(name: str):
    path = ROOT / "evals" / "designer" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"designer_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_claims = _load("build_claims")

RUN = {"run_id": "run-1", "prd": "prd.md"}


def _claim(claim_id: str, span_id: str, requirement_id: str = "FR-ACC-01") -> dict:
    return {
        "kind": "claim",
        "target_id": claim_id,
        "span_id": span_id,
        "attributes": {
            "claim.requirement_id": requirement_id,
            "claim.case_id": claim_id.split("->")[0],
            "output.value": f"## Case: {claim_id}",
        },
    }


def _requirement(span_id: str) -> dict:
    return {"kind": "requirement", "target_id": "FR-ACC-01", "span_id": span_id, "attributes": {}}


def _label(span_id: str, name: str, label: str | None = None, explanation: str | None = None):
    return {
        "span_id": span_id,
        "annotation": name,
        "annotator_kind": "HUMAN",
        "label": label,
        "explanation": explanation,
    }


def test_build_rows_joins_claim_units_with_human_labels():
    units = [_requirement("req-1"), _claim("case-1->FR-ACC-01", "span-1")]
    labels = [
        _label("span-1", "claim_alignment", "pass"),
        _label("req-1", "claim_alignment", "pass"),
        {"span_id": "span-1", "annotation": "case_duplicate", "annotator_kind": "CODE"},
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
