"""Judge one designer claim against the PRD."""

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings

from evals.designer.designer_eval.dataset import load_dataset
from evals.designer.designer_eval.jsonl import write_rows
from evals.designer.designer_eval.metrics import wilson_interval
from evals.designer.designer_eval.requirements import parse_requirements

SYSTEM_PROMPT = """\
You are a senior QA reviewer. You judge one generated test case against a PRD. The case claims one
requirement. Decide one thing: does the case verify that requirement — is every behaviour assertion
in it stated in the PRD and produced by a step of the case (or global state), and is every result
the requirement states asserted by some step?

Read the whole PRD, the claimed requirement, and the case. Audit every step and return one `checks`
entry per step: the step number, whether its expected_result is grounded in the PRD and verifies the
claimed requirement, and a short note. A step is not grounded when it asserts a value the PRD never
states, behaviour that no step of this case produces, or something that cannot be decided. If any
check is not grounded, the result is fail.

Fail when any of these is true:
1. The steps never perform the claimed requirement's scenario, or the case's preconditions already
   did.
2. Any expected_result asserts behaviour the whole PRD does not state, or cannot be decided. A
   specific value (a default, a limit, persistence, a message) that the PRD never states is a
   failure even when the rest of the case is correct.
3. An assertion names behaviour that no step of this case produces and that is not global state.
   Asserting a result your own step produces is allowed, even when the PRD defines that result under
   another requirement.
4. The case performs the scenario but never asserts a result the claimed requirement states. Page
   furniture, field lists, element presence, and form-field mechanics are not results.

These are not assertions: a step that only sets up state, a step that only cleans up or logs out, a
value introduced with "e.g.", page or context assertions, form-field input mechanics, element
presence, and "no error" clauses. Repeating a stated rule with a different input is the same rule,
not a new assertion. A parenthetical that explains why a stated result matters is not an assertion.

The case's scenario title may name another requirement; judge the steps, not the title. Judge only
the claimed requirement. Do not name a failure mode. Write the critique first, then the result.
"""


class StepCheck(BaseModel):
    step: int
    grounded: bool
    note: str


class JudgeOutput(BaseModel):
    checks: list[StepCheck]
    critique: str
    result: Literal["pass", "fail"]


@dataclass(frozen=True)
class JudgeInput:
    source_run: str
    claim_id: str
    requirement_id: str
    case_id: str
    prd_text: str
    requirement_text: str
    case_markdown: str


@dataclass(frozen=True)
class JudgeExample:
    data: JudgeInput
    human_label: str
    human_mode: str | None


class JudgeRecord(BaseModel):
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


def prompt_sha256() -> str:
    return hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()


def build_prompt(example: JudgeExample) -> str:
    data = example.data
    return (
        f"# PRD\n\n{data.prd_text}\n\n"
        f"# Claimed requirement\n\n{data.requirement_id}\n{data.requirement_text}\n\n"
        f"# Case\n\n{data.case_markdown}\n"
    )


def load_examples(data_dir: Path, *, single_fr_only: bool = True) -> list[JudgeExample]:
    """Turn a dataset's rows into judge inputs; the PRD supplies each requirement's text."""
    dataset = load_dataset(data_dir, single_fr_only=single_fr_only)
    requirement_text = {
        requirement.id: requirement.text for requirement in parse_requirements(dataset.prd_text)
    }
    examples = [
        JudgeExample(
            data=JudgeInput(
                source_run=claim.source_run,
                claim_id=claim.claim_id,
                requirement_id=claim.requirement_id,
                case_id=claim.case_id,
                prd_text=dataset.prd_text,
                requirement_text=requirement_text[claim.requirement_id],
                case_markdown=claim.case_markdown,
            ),
            human_label=claim.human_label,
            human_mode=claim.human_mode,
        )
        for claim in dataset.claims
    ]
    return sorted(examples, key=lambda example: example.data.claim_id)


async def run_one(
    agent: Agent[None, JudgeOutput],
    example: JudgeExample,
    *,
    model_name: str,
    temperature: float | None = None,
) -> JudgeRecord:
    settings = ModelSettings(temperature=temperature) if temperature is not None else None
    result = await agent.run(build_prompt(example), model_settings=settings)
    output = result.output
    data = example.data
    return JudgeRecord(
        claim_id=data.claim_id,
        source_run=data.source_run,
        requirement_id=data.requirement_id,
        case_id=data.case_id,
        verdict=output.result,
        critique=output.critique,
        checks=[check.model_dump() for check in output.checks],
        human_label=example.human_label,
        human_mode=example.human_mode,
        model=model_name,
        prompt_sha256=prompt_sha256(),
    )


def score(records: Sequence[JudgeRecord]) -> JudgeMetrics:
    caught = missed = false_alarm = agreed_pass = 0
    disagreements: list[JudgeRecord] = []
    for record in records:
        human_fail = record.human_label == "fail"
        judge_fail = record.verdict == "fail"
        if human_fail and judge_fail:
            caught += 1
        elif human_fail and not judge_fail:
            missed += 1
        elif not human_fail and judge_fail:
            false_alarm += 1
        else:
            agreed_pass += 1
        if human_fail != judge_fail:
            disagreements.append(record)
    human_fail_total = caught + missed
    human_pass_total = false_alarm + agreed_pass
    return JudgeMetrics(
        total=len(records),
        human_fail=human_fail_total,
        human_pass=human_pass_total,
        judged_fail=caught + false_alarm,
        judged_pass=missed + agreed_pass,
        caught=caught,
        missed=missed,
        false_alarm=false_alarm,
        agreed_pass=agreed_pass,
        fail_recall=caught / human_fail_total if human_fail_total else None,
        pass_specificity=agreed_pass / human_pass_total if human_pass_total else None,
        fail_recall_ci=wilson_interval(caught, human_fail_total) if human_fail_total else None,
        pass_specificity_ci=(
            wilson_interval(agreed_pass, human_pass_total) if human_pass_total else None
        ),
        disagreements=disagreements,
    )


def group_by_source(records: Sequence[JudgeRecord]) -> dict[str, JudgeMetrics]:
    groups: dict[str, list[JudgeRecord]] = {}
    for record in records:
        groups.setdefault(record.source_run, []).append(record)
    return {source: score(group) for source, group in sorted(groups.items())}


def format_rate(value: float | None, interval: tuple[float, float] | None) -> str:
    if value is None or interval is None:
        return "n/a"
    return f"{value:.2f} [{interval[0]:.2f}, {interval[1]:.2f}]"


def render_report(metrics: JudgeMetrics, groups: dict[str, JudgeMetrics] | None = None) -> str:
    lines = [
        "# Designer judge report",
        "",
        f"- Claims: {metrics.total}",
        f"- Human labels: {metrics.human_fail} fail, {metrics.human_pass} pass",
        f"- Judge verdicts: {metrics.judged_fail} fail, {metrics.judged_pass} pass",
        "",
        "## Metrics",
        "",
        "| Metric | Definition | Value (Wilson 95% CI) |",
        "| --- | --- | --- |",
        (
            f"| Fail recall | judge fails when the human fails | "
            f"{format_rate(metrics.fail_recall, metrics.fail_recall_ci)} |"
        ),
        (
            f"| Pass specificity | judge passes when the human passes | "
            f"{format_rate(metrics.pass_specificity, metrics.pass_specificity_ci)} |"
        ),
        "",
        "## Confusion",
        "",
        "| | human fail | human pass |",
        "| --- | --- | --- |",
        f"| judge fail | {metrics.caught} | {metrics.false_alarm} |",
        f"| judge pass | {metrics.missed} | {metrics.agreed_pass} |",
        "",
    ]
    if groups and len(groups) > 1:
        lines += [
            "## By source run",
            "",
            "| source run | claims | fail recall | pass specificity |",
            "| --- | --- | --- | --- |",
        ]
        for source, group in groups.items():
            lines.append(
                f"| `{source}` | {group.total} | "
                f"{format_rate(group.fail_recall, group.fail_recall_ci)} | "
                f"{format_rate(group.pass_specificity, group.pass_specificity_ci)} |"
            )
        lines.append("")
    lines += ["## Disagreements", ""]
    if not metrics.disagreements:
        lines.append("None.")
    for record in metrics.disagreements:
        lines.append(
            f"- `{record.claim_id}` ({record.source_run}): human `{record.human_label}`"
            + (f" / {record.human_mode}" if record.human_mode else "")
            + f", judge `{record.verdict}` - {record.critique.strip().splitlines()[0][:160]}"
        )
    lines += [
        "",
        "## Limits",
        "",
        "- Dev only: every dataset holds one PRD, so these rates cannot be a held-out estimate.",
        "- A rate is `n/a` when the human labels contain no example of that class.",
        "- Legacy multi-requirement cases are excluded unless `--include-multi-fr` is passed.",
    ]
    return "\n".join(lines) + "\n"


def write_records(path: Path, records: Sequence[JudgeRecord]) -> None:
    write_rows(path, records)
