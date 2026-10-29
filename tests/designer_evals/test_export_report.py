import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[2]


def _load(name: str):
    path = ROOT / ".scratch" / "designer-evals" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"designer_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


export_labels = _load("export_labels")
report = _load("report")


def _run():
    return {"run_id": "run-1", "prd": "register-login.md", "model": "model-1"}


def _claim(target_id: str, span_id: str, requirement_id: str, case_id: str):
    return {
        "kind": "claim",
        "target_id": target_id,
        "span_id": span_id,
        "name": f"claim {target_id}",
        "attributes": {
            "claim.requirement_exists": "true",
            "requirement.id": requirement_id,
            "claim.case_id": case_id,
        },
    }


def _human(target_id: str, span_id: str, label: str):
    return {
        "run_id": "run-1",
        "prd": "register-login.md",
        "target_kind": "claim",
        "target_id": target_id,
        "span_id": span_id,
        "annotation": "claim_alignment",
        "annotator_kind": "HUMAN",
        "label": label,
        "score": 1.0 if label == "pass" else 0.0,
        "annotator": "local",
        "explanation": None,
        "identifier": "",
        "annotation_id": f"annotation-{target_id}",
        "source": "APP",
        "metadata": {},
    }


def test_export_label_rows_keeps_human_and_code_annotations():
    units = [_claim("FR-1<-case-1", "span-1", "FR-1", "case-1")]
    annotations = [
        {
            "id": "a1",
            "span_id": "span-1",
            "name": "claim_alignment",
            "annotator_kind": "HUMAN",
            "result": {"label": "pass", "score": 1.0, "explanation": None},
            "identifier": "",
            "source": "APP",
            "metadata": {},
        },
        {
            "id": "a2",
            "span_id": "span-1",
            "name": "case_duplicate",
            "annotator_kind": "CODE",
            "result": {"label": "unique", "score": 1.0, "explanation": None},
            "identifier": "",
            "source": "API",
            "metadata": {"case_id": "case-1"},
        },
    ]

    rows = export_labels._label_rows(units, annotations, _run(), annotator="local")

    assert len(rows) == 2
    human = next(row for row in rows if row["annotator_kind"] == "HUMAN")
    code = next(row for row in rows if row["annotator_kind"] == "CODE")
    assert human["annotator"] == "local"
    assert human["target_id"] == "FR-1<-case-1"
    assert code["annotator"] == "code"
    assert code["metadata"] == {"case_id": "case-1"}


def test_requirement_rows_marks_a_fake_failure_as_false_tag():
    units = [
        _claim("FR-1<-case-1", "span-1", "FR-1", "case-1"),
        _claim("FR-2<-case-2", "span-2", "FR-2", "case-2"),
    ]
    labels = [
        _human("FR-1<-case-1", "span-1", "pass"),
        _human("FR-2<-case-2", "span-2", "fail"),
    ]

    rows, invented = report.requirement_rows(units, labels)

    assert invented == []
    assert {row["requirement_id"]: row["status"] for row in rows} == {
        "FR-1": "covered",
        "FR-2": "not_covered",
    }
    assert rows[1]["pass_count"] == 0


def test_requirement_rows_separates_missing_and_invented():
    units = [
        {
            "kind": "requirement",
            "target_id": "FR-3",
            "span_id": "span-3",
            "name": "requirement FR-3 (missing)",
            "attributes": {"requirement.missing": "true", "requirement.id": "FR-3"},
        },
        {
            "kind": "claim",
            "target_id": "FR-9<-case-1",
            "span_id": "span-9",
            "name": "claim FR-9 <- case-1 (invented)",
            "attributes": {
                "claim.requirement_exists": "false",
                "requirement.id": "FR-9",
                "claim.case_id": "case-1",
            },
        },
    ]

    rows, invented = report.requirement_rows(units, [])

    assert [row["status"] for row in rows] == ["missing"]
    assert invented == ["FR-9<-case-1"]


def test_wilson_interval_for_six_of_six():
    low, high = report.wilson_interval(6, 6)

    assert 0.609 < low < 0.611
    assert high > 0.999


def test_render_report_shows_fake_failure(tmp_path):
    units = [
        _claim("FR-1<-case-1", "span-1", "FR-1", "case-1"),
        _claim("FR-2<-case-2", "span-2", "FR-2", "case-2"),
    ]
    labels = [
        _human("FR-1<-case-1", "span-1", "pass"),
        _human("FR-2<-case-2", "span-2", "fail"),
    ]
    design = {
        "cases": [
            {"requirement_ids": ["FR-1"]},
            {"requirement_ids": ["FR-2"]},
        ]
    }

    text = report.render_report(
        run=_run(),
        units=units,
        labels=labels,
        design=design,
        structure_errors=["front_matter: missing"],
    )

    assert "Covered: 1 / 2 (50%)" in text
    assert "Not covered: 1" in text
    assert "FR-2: FR-2<-case-2=fail" in text
    assert "Structure failures: 1" in text
