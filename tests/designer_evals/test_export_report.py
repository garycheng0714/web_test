import importlib.util
from pathlib import Path

ROOT = Path(__file__).parents[2]


def _load(name: str):
    path = ROOT / "evals" / "designer" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"designer_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


export_labels = _load("export_labels")
report = _load("report")


def _run():
    return {"run_id": "run-1", "prd": "register-login.md", "model": "model-1"}


def _requirement(requirement_id: str, span_id: str, *, missing: bool = False):
    return {
        "kind": "requirement",
        "target_id": requirement_id,
        "span_id": span_id,
        "name": f"requirement {requirement_id}",
        "attributes": {
            "requirement.id": requirement_id,
            "requirement.missing": "true" if missing else "false",
        },
    }


def _claim(target_id: str, span_id: str, requirement_id: str, case_id: str):
    return {
        "kind": "claim",
        "target_id": target_id,
        "span_id": span_id,
        "name": f"claim {target_id}",
        "attributes": {
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


def _design_case(requirement_ids: list[str], **overrides):
    return {
        "requirement_ids": requirement_ids,
        "module_feature": "Account",
        "test_scenario": "Register",
        "preconditions": [],
        "steps": [{"action": "Sign up", "expected_result": "Account page shown"}],
        "priority": "High",
        "severity": "Major",
        "test_type": "Functional",
        **overrides,
    }


def _human_note(target_id: str, span_id: str, annotation: str, text: str):
    row = _human(target_id, span_id, "fail")
    row["annotation"] = annotation
    row["label"] = None
    row["score"] = None
    row["explanation"] = text
    return row


def _human_label(target_id: str, span_id: str, annotation: str, label: str):
    row = _human(target_id, span_id, label)
    row["annotation"] = annotation
    return row


def _annotation(span_id: str, name: str, label=None, explanation=None):
    return {
        "id": f"a-{name}-{span_id}",
        "span_id": span_id,
        "name": name,
        "annotator_kind": "HUMAN",
        "result": {"label": label, "score": None, "explanation": explanation},
        "identifier": "",
        "source": "APP",
        "metadata": {},
    }


def test_export_label_rows_keeps_human_and_code_annotations():
    units = [
        _requirement("FR-1", "span-0"),
        _claim("case-1-functional->FR-1", "span-1", "FR-1", "case-1-functional"),
    ]
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
            "metadata": {"case_id": "case-1-functional"},
        },
    ]

    rows = export_labels._label_rows(units, annotations, _run(), annotator="local")

    assert len(rows) == 2
    human = next(row for row in rows if row["annotator_kind"] == "HUMAN")
    code = next(row for row in rows if row["annotator_kind"] == "CODE")
    assert human["annotator"] == "local"
    assert human["target_id"] == "case-1-functional->FR-1"
    assert code["annotator"] == "code"
    assert code["metadata"] == {"case_id": "case-1-functional"}


def test_export_drops_failure_mode_on_a_passing_claim():
    units = [
        _requirement("FR-1", "span-0"),
        _claim("case-1-functional->FR-1", "span-1", "FR-1", "case-1-functional"),
    ]
    annotations = [
        _annotation("span-1", "claim_alignment", "pass"),
        _annotation("span-1", "claim_failure_mode", "N/A"),
        _annotation("span-1", "claim_reason", explanation="teardown note"),
    ]

    rows = export_labels._label_rows(units, annotations, _run(), annotator="local")

    names = [row["annotation"] for row in rows]
    assert "claim_failure_mode" not in names
    assert "claim_reason" in names
    assert "claim_alignment" in names


def test_export_keeps_failure_mode_on_a_failing_claim():
    units = [
        _requirement("FR-1", "span-0"),
        _claim("case-1-functional->FR-1", "span-1", "FR-1", "case-1-functional"),
    ]
    annotations = [
        _annotation("span-1", "claim_alignment", "fail"),
        _annotation("span-1", "claim_failure_mode", "duplicated"),
    ]

    rows = export_labels._label_rows(units, annotations, _run(), annotator="local")

    assert "claim_failure_mode" in [row["annotation"] for row in rows]


def test_requirement_rows_marks_a_fake_failure_as_false_tag():
    units = [
        _requirement("FR-1", "span-0"),
        _requirement("FR-2", "span-00"),
        _claim("case-1-functional->FR-1", "span-1", "FR-1", "case-1-functional"),
        _claim("case-2-functional->FR-2", "span-2", "FR-2", "case-2-functional"),
    ]
    labels = [
        _human("case-1-functional->FR-1", "span-1", "pass"),
        _human("case-2-functional->FR-2", "span-2", "fail"),
    ]

    rows = report.requirement_rows(units, labels)

    assert {row["requirement_id"]: row["status"] for row in rows} == {
        "FR-1": "covered",
        "FR-2": "not_clean",
    }
    assert rows[1]["pass_count"] == 0


def test_requirement_rows_marks_a_missing_requirement():
    units = [_requirement("FR-3", "span-3", missing=True)]

    rows = report.requirement_rows(units, [])

    assert [row["status"] for row in rows] == ["missing"]


def test_wilson_interval_for_six_of_six():
    low, high = report.wilson_interval(6, 6)

    assert 0.609 < low < 0.611
    assert high > 0.999


def test_render_report_shows_fake_failure(tmp_path):
    units = [
        _requirement("FR-1", "span-0"),
        _requirement("FR-2", "span-00"),
        _claim("case-1-functional->FR-1", "span-1", "FR-1", "case-1-functional"),
        _claim("case-2-functional->FR-2", "span-2", "FR-2", "case-2-functional"),
    ]
    labels = [
        _human("case-1-functional->FR-1", "span-1", "pass"),
        _human("case-2-functional->FR-2", "span-2", "fail"),
    ]
    design = {"cases": [_design_case(["FR-1"]), _design_case(["FR-2"])]}

    text = report.render_report(
        run=_run(),
        units=units,
        labels=labels,
        design=design,
        structure_errors=["front_matter: missing"],
        findings=report.RunFindings(
            non_requirement_ids={"case-1-functional": ["MSG-TITLE"]},
            invalid_requirement_ids={"case-2-functional": ["FR-999"]},
            multi_requirement_cases=["case-2-functional"],
        ),
    )

    assert "Tested: 2 / 2" in text
    assert "Clean: 1 / 2 (50%)" in text
    assert "Not clean: 1" in text
    assert "case-2-functional->FR-2=fail" in text
    assert "Structure failures: 1" in text
    assert "Non-requirement IDs: 1" in text
    assert "Invalid requirement IDs: 1" in text
    assert "Multi-requirement cases: 1" in text


def test_render_report_counts_only_claim_alignment_as_a_human_label():
    units = [
        _requirement("FR-1", "span-0"),
        _claim("case-1-functional->FR-1", "span-1", "FR-1", "case-1-functional"),
    ]
    labels = [
        _human("case-1-functional->FR-1", "span-1", "fail"),
        _human_label(
            "case-1-functional->FR-1",
            "span-1",
            "claim_failure_mode",
            "wrong_assertion_to_requirement",
        ),
        _human_note("case-1-functional->FR-1", "span-1", "claim_reason", "extra cart step"),
    ]

    text = report.render_report(
        run=_run(),
        units=units,
        labels=labels,
        design={"cases": [_design_case(["FR-1"])]},
    )

    assert "HUMAN labels: 1" in text
    assert "| wrong_assertion_to_requirement | 1 |" in text
    assert "| fail (total) | 1 |" in text
    assert "extra cart step" in text


def test_render_report_flags_duplicates_without_claims():
    design = {"cases": [_design_case([]), _design_case([])]}

    text = report.render_report(run=_run(), units=[], labels=[], design=design)

    assert "Duplicate cases: 2 (case-1-functional, case-2-functional)" in text


def test_empty_cases_uses_the_case_id_format():
    design = {
        "cases": [
            _design_case([], test_type="DataPersistence"),
            _design_case(["FR-1"]),
        ]
    }

    assert report._empty_cases(design) == ["case-1-data-persistence"]


def test_render_report_names_why_structure_checks_were_skipped():
    text = report.render_report(
        run=_run(),
        units=[],
        labels=[],
        design={"cases": []},
        structure_note="test-case.md is missing",
    )

    assert "Structure failures: not checked (test-case.md is missing)" in text


def test_render_report_separates_tested_from_clean():
    units = [
        _requirement("FR-1", "span-0"),
        _claim("case-1-functional->FR-1", "span-1", "FR-1", "case-1-functional"),
    ]
    labels = [_human("case-1-functional->FR-1", "span-1", "fail")]

    text = report.render_report(
        run=_run(),
        units=units,
        labels=labels,
        design={"cases": [_design_case(["FR-1"])]},
    )

    assert "Tested: 1 / 1" in text
    assert "Clean: 0 / 1 (0%)" in text
    assert "Not clean: 1" in text
    assert "Structure failures: not checked" in text
