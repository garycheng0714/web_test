import json
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from evals.designer.designer_eval.judge import (
    SYSTEM_PROMPT,
    JudgeExample,
    JudgeInput,
    JudgeOutput,
    JudgeRecord,
    build_prompt,
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
    (tmp_path / "prd.md").write_text("# PRD\n", encoding="utf-8")
    row = {
        "source_run": "run-1",
        "claim_id": "case-1-functional->FR-1",
        "requirement_id": "FR-1",
        "case_id": "case-1-functional",
        "requirement_text": "### FR-1",
        "case_markdown": "## Case 1",
        "human_label": "fail",
        "human_mode": "duplicated",
        "human_reason": None,
    }
    (tmp_path / "claims.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")

    examples = load_examples(tmp_path)

    assert len(examples) == 1
    assert examples[0].data.prd_text == "# PRD\n"
    assert examples[0].human_label == "fail"
    assert examples[0].human_mode == "duplicated"


def test_score_computes_tpr_and_tnr():
    records = [
        _record("fail", "fail"),
        _record("fail", "fail"),
        _record("pass", "fail"),
        _record("pass", "pass"),
        _record("fail", "pass"),
    ]

    metrics = score(records)

    assert (metrics.total, metrics.passed, metrics.failed) == (5, 2, 3)
    assert metrics.tpr == 2 / 3
    assert metrics.tnr == 1 / 2
    assert [record.verdict for record in metrics.disagreements] == ["pass", "fail"]


def test_run_one_uses_the_structured_output():
    model = TestModel(custom_output_args={"critique": "extra step", "result": "fail"})
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
    assert "TPR" in text
    assert "asserts an undefined behaviour" in text
    assert "Dev split only" in text
