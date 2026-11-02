"""Judge one designer claim against the PRD."""

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent

from evals.designer.designer_eval.metrics import wilson_interval

SYSTEM_PROMPT = """\
You are a senior QA reviewer. You judge one generated test case against a PRD. The case claims
one requirement; decide whether it is a valid verification of that requirement.

Read the whole PRD, the claimed requirement, and the case. Check every step's expected_result one
by one. Fail when any of these is true:
1. The steps never perform the claimed requirement's scenario.
2. Any expected_result asserts behaviour the whole PRD does not state, or cannot be decided. A
   specific value (a default, a limit, persistence, a message) that the PRD never states is a
   failure even when the rest of the case is correct.
3. An assertion does not verify the claimed requirement's body or acceptance criteria.
4. The case lists several requirements and this one has no scenario of its own: the case's primary
   flow belongs to another claimed requirement and this requirement's acceptance criteria only
   appear as a side assertion (duplicated). Use the case's requirement_ids to spot this.

The case's scenario title may name another requirement; judge the steps, not the title. A step
that only sets up state is not an assertion. Values introduced with "e.g." are examples, not
assertions. Ignore page or context assertions, form-field input mechanics, element presence, and
"no error" clauses. Judge only the claimed requirement.
Do not name a failure mode. Write the critique first, then the result.
"""


class JudgeOutput(BaseModel):
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
    human_label: str
    human_mode: str | None
    model: str
    prompt_sha256: str


@dataclass(frozen=True)
class JudgeMetrics:
    total: int
    passed: int
    failed: int
    tpr: float
    tnr: float
    tpr_ci: tuple[float, float]
    tnr_ci: tuple[float, float]
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


def load_examples(data_dir: Path) -> list[JudgeExample]:
    prd_text = (data_dir / "prd.md").read_text(encoding="utf-8")
    examples: list[JudgeExample] = []
    for line in (data_dir / "claims.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        examples.append(
            JudgeExample(
                data=JudgeInput(
                    source_run=row["source_run"],
                    claim_id=row["claim_id"],
                    requirement_id=row["requirement_id"],
                    case_id=row["case_id"],
                    prd_text=prd_text,
                    requirement_text=row["requirement_text"],
                    case_markdown=row["case_markdown"],
                ),
                human_label=row["human_label"],
                human_mode=row.get("human_mode"),
            )
        )
    return sorted(examples, key=lambda example: example.data.claim_id)


async def run_one(
    agent: Agent[None, JudgeOutput],
    example: JudgeExample,
    *,
    model_name: str,
) -> JudgeRecord:
    result = await agent.run(build_prompt(example))
    output = result.output
    data = example.data
    return JudgeRecord(
        claim_id=data.claim_id,
        source_run=data.source_run,
        requirement_id=data.requirement_id,
        case_id=data.case_id,
        verdict=output.result,
        critique=output.critique,
        human_label=example.human_label,
        human_mode=example.human_mode,
        model=model_name,
        prompt_sha256=prompt_sha256(),
    )


def score(records: Sequence[JudgeRecord]) -> JudgeMetrics:
    tp = tn = fp = fn = 0
    disagreements: list[JudgeRecord] = []
    for record in records:
        human_fail = record.human_label == "fail"
        judge_fail = record.verdict == "fail"
        if human_fail and judge_fail:
            tp += 1
        elif human_fail and not judge_fail:
            fn += 1
        elif not human_fail and judge_fail:
            fp += 1
        else:
            tn += 1
        if human_fail != judge_fail:
            disagreements.append(record)
    tpr = tp / (tp + fn) if tp + fn else 0.0
    tnr = tn / (tn + fp) if tn + fp else 0.0
    return JudgeMetrics(
        total=len(records),
        passed=sum(record.verdict == "pass" for record in records),
        failed=sum(record.verdict == "fail" for record in records),
        tpr=tpr,
        tnr=tnr,
        tpr_ci=wilson_interval(tp, tp + fn),
        tnr_ci=wilson_interval(tn, tn + fp),
        disagreements=disagreements,
    )


def render_report(metrics: JudgeMetrics) -> str:
    lines = [
        "# Designer judge report",
        "",
        f"- Claims: {metrics.total}",
        f"- Judge verdicts: {metrics.passed} pass, {metrics.failed} fail",
        "",
        "## Metrics",
        "",
        "| Metric | Value | Wilson 95% CI |",
        "| --- | --- | --- |",
        f"| TPR | {metrics.tpr:.2f} | [{metrics.tpr_ci[0]:.2f}, {metrics.tpr_ci[1]:.2f}] |",
        f"| TNR | {metrics.tnr:.2f} | [{metrics.tnr_ci[0]:.2f}, {metrics.tnr_ci[1]:.2f}] |",
        "",
        "## Disagreements",
        "",
    ]
    if not metrics.disagreements:
        lines.append("None.")
    for record in metrics.disagreements:
        lines.append(
            f"- `{record.claim_id}`: human `{record.human_label}`"
            + (f" / {record.human_mode}" if record.human_mode else "")
            + f", judge `{record.verdict}` - {record.critique.strip().splitlines()[0][:160]}"
        )
    lines += [
        "",
        "## Limits",
        "",
        "- Dev split only: the labeled data comes from one PRD. Do not read TPR/TNR as a",
        "  general estimate until there are 5-6 PRDs for a by-PRD split.",
    ]
    return "\n".join(lines) + "\n"


def write_records(path: Path, records: Sequence[JudgeRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(record.model_dump_json(exclude_none=False) + "\n" for record in records),
        encoding="utf-8",
    )
