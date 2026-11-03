import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from evals.designer.designer_eval.judge import (
    SYSTEM_PROMPT,
    JudgeExample,
    JudgeInput,
    JudgeOutput,
    JudgeRecord,
    build_prompt,
    group_by_source,
    load_examples,
    prompt_sha256,
    render_report,
    run_one,
    score,
    write_records,
)
from web_test._run import run_sync


def _example(human_label: str = "pass", human_mode: str | None = None) -> JudgeExample:
    return JudgeExample(
        data=JudgeInput(
            source_run="run-1",
            claim_id="case-1-functional->FR-1",
            requirement_id="FR-1",
            case_id="case-1-functional",
            prd_text="# PRD\n\nFR-1: a user can sign up.",
            requirement_text="### FR-1\n- a user can sign up",
            case_markdown="## Case 1: sign up\n\n| Step | Action | Expected Result |",
        ),
        human_label=human_label,
        human_mode=human_mode,
    )


def _record(verdict: str, human_label: str, critique: str = "because") -> JudgeRecord:
    return JudgeRecord(
        claim_id="case-1-functional->FR-1",
        source_run="run-1",
        requirement_id="FR-1",
        case_id="case-1-functional",
        verdict=verdict,
        critique=critique,
        checks=[],
        human_label=human_label,
        human_mode=None,
        model="test-model",
        prompt_sha256="hash",
    )


def test_build_prompt_contains_the_prd_requirement_and_case():
    prompt = build_prompt(_example())

    assert "# PRD" in prompt
    assert "FR-1: a user can sign up." in prompt
    assert "### FR-1" in prompt
    assert "## Case 1: sign up" in prompt
    assert "human_label" not in prompt


def test_load_examples_reads_the_dataset(tmp_path: Path):
    (tmp_path / "prd.md").write_text("#### FR-ACC-01 sign up\n\n- **AC-1**: a user can sign up.\n")
    row = {
        "source_run": "run-1",
        "claim_id": "case-1-functional->FR-ACC-01",
        "requirement_id": "FR-ACC-01",
        "case_id": "case-1-functional",
        "case_markdown": "## Case 1",
        "human_label": "fail",
        "human_mode": "duplicated",
        "human_reason": None,
    }
    (tmp_path / "claims.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")

    examples = load_examples(tmp_path)

    assert len(examples) == 1
    assert examples[0].data.prd_text.startswith("#### FR-ACC-01")
    assert examples[0].data.requirement_text.startswith("#### FR-ACC-01 sign up")
    assert examples[0].human_label == "fail"
    assert examples[0].human_mode == "duplicated"


def test_load_examples_rejects_a_requirement_the_prd_does_not_define(tmp_path: Path):
    _write_claims(
        tmp_path,
        [
            {
                "source_run": "run-1",
                "claim_id": "case-1-functional->FR-ACC-99",
                "requirement_id": "FR-ACC-99",
                "case_id": "case-1-functional",
                "case_markdown": "## Case 1: sign up",
                "human_label": "pass",
            }
        ],
    )

    with pytest.raises(ValueError, match="FR-ACC-99"):
        load_examples(tmp_path)


def _write_claims(tmp_path: Path, rows: list[dict[str, object]]) -> None:
    (tmp_path / "prd.md").write_text("#### FR-ACC-01 sign up\n\n- **AC-1**: a user can sign up.\n")
    (tmp_path / "claims.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )


def test_load_examples_skips_multi_requirement_cases(tmp_path: Path):
    case = "## Case 1: sign up\n\n```yaml\nrequirement_ids: [FR-ACC-01, FR-ACC-02]\n```\n"
    _write_claims(
        tmp_path,
        [
            {
                "source_run": "run-1",
                "claim_id": "case-1-functional->FR-ACC-01",
                "requirement_id": "FR-ACC-01",
                "case_id": "case-1-functional",
                "case_markdown": case,
                "human_label": "fail",
            }
        ],
    )

    assert load_examples(tmp_path) == []
    assert len(load_examples(tmp_path, single_fr_only=False)) == 1


def test_load_examples_rejects_an_unknown_label(tmp_path: Path):
    _write_claims(
        tmp_path,
        [
            {
                "source_run": "run-1",
                "claim_id": "case-1-functional->FR-ACC-01",
                "requirement_id": "FR-ACC-01",
                "case_id": "case-1-functional",
                "case_markdown": "## Case 1: sign up",
                "human_label": "Not quite",
            }
        ],
    )

    with pytest.raises(ValidationError):
        load_examples(tmp_path)


def test_score_computes_fail_recall_and_pass_specificity():
    records = [
        _record("fail", "fail"),
        _record("fail", "fail"),
        _record("pass", "fail"),
        _record("pass", "pass"),
        _record("fail", "pass"),
    ]

    metrics = score(records)

    assert (metrics.total, metrics.human_fail, metrics.human_pass) == (5, 3, 2)
    assert (metrics.judged_fail, metrics.judged_pass) == (3, 2)
    confusion = (metrics.caught, metrics.missed, metrics.false_alarm, metrics.agreed_pass)
    assert confusion == (2, 1, 1, 1)
    assert metrics.fail_recall == 2 / 3
    assert metrics.pass_specificity == 1 / 2
    assert [record.verdict for record in metrics.disagreements] == ["pass", "fail"]


def test_score_reports_an_absent_class_as_none():
    metrics = score([_record("pass", "pass")])

    assert metrics.fail_recall is None
    assert metrics.fail_recall_ci is None
    assert metrics.pass_specificity == 1.0
    assert "n/a" in render_report(metrics)


def test_group_by_source_splits_the_metrics():
    records = [
        _record("fail", "fail"),
        JudgeRecord(
            claim_id="case-2-functional->FR-2",
            source_run="run-2",
            requirement_id="FR-2",
            case_id="case-2-functional",
            verdict="pass",
            critique="fine",
            checks=[],
            human_label="pass",
            human_mode=None,
            model="test-model",
            prompt_sha256="hash",
        ),
    ]

    groups = group_by_source(records)

    assert set(groups) == {"run-1", "run-2"}
    assert groups["run-1"].fail_recall == 1.0
    assert groups["run-2"].pass_specificity == 1.0
    report = render_report(score(records), groups)
    assert "By source run" in report
    assert "| `run-2` | 1 |" in report


def test_run_one_uses_the_structured_output():
    model = TestModel(
        custom_output_args={
            "checks": [{"step": 1, "grounded": False, "note": "defaults are not in the PRD"}],
            "critique": "extra step",
            "result": "fail",
        }
    )
    agent = Agent(model, output_type=JudgeOutput, instructions=SYSTEM_PROMPT)

    record = run_sync(run_one(agent, _example(), model_name="test-model"))

    assert record.verdict == "fail"
    assert record.critique == "extra step"
    assert record.prompt_sha256 == prompt_sha256()
    assert record.human_label == "pass"


def test_write_records_and_render_report(tmp_path: Path):
    records = [_record("fail", "pass", critique="asserts an undefined behaviour")]

    write_records(tmp_path / "judgements.jsonl", records)
    text = render_report(score(records))

    written = [
        json.loads(line) for line in (tmp_path / "judgements.jsonl").read_text().splitlines()
    ]
    assert written[0]["verdict"] == "fail"
    assert "Fail recall" in text
    assert "asserts an undefined behaviour" in text
    assert "Dev only" in text
