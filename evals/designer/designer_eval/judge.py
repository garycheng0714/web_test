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
from evals.designer.designer_eval.judge_records import JudgeMetrics, JudgeRecord
from evals.designer.designer_eval.metrics import wilson_interval
from evals.designer.designer_eval.requirements import parse_requirements

SYSTEM_PROMPT = """\
You are a senior QA reviewer. You judge one generated test case against a PRD. The case claims one
requirement. Decide one thing: does the case verify that requirement — is every behaviour assertion
in it stated in the PRD or the ordinary consequence of a stated result, and produced by a step of
the case (or global state), and is every result the requirement states asserted by some step?

Read the whole PRD, the claimed requirement, and the case. Audit every step and return one `checks`
entry per step: the step number, `grounded`, and a short note. `grounded` is true when the
expected_result is stated in the PRD and verifies the claimed requirement, or is an ordinary
consequence of such a result; false when it asserts a value the PRD never states, behaviour that no
step of this case produces, or something that cannot be decided; and null when the expected_result
is only one of the non-assertions below, because there is nothing to ground. If any check is false,
the result is fail.

Fail when any of these is true:
1. The steps never perform the claimed requirement's scenario, or the case's preconditions already
   did.
2. An expected_result that is an assertion states behaviour the PRD does not state and that is not
   the ordinary consequence of a stated result, or cannot be decided. A specific value (a default,
   a limit, a message) that the PRD never states is a failure even when the rest of the case is
   correct.
3. An assertion names behaviour that no step of this case produces and that is not global state.
   Asserting a result your own step produces is allowed, even when the PRD defines that result under
   another requirement.
4. The case performs the scenario but never asserts a result the claimed requirement states. Page
   furniture, field lists, element presence, and form-field mechanics are not results.

A consequence is ordinary when the PRD states that an action succeeds and the assertion is what that
success necessarily produces: the change is persisted, the form or page is left, the created item
exists afterwards. This does not license behaviour the PRD marks as unspecified, and it does not
license a value, message or permission the PRD never states.

These are not assertions: a step that only sets up state, a step that only cleans up or logs out, a
value introduced with "e.g.", page or context assertions, form-field input mechanics, element
presence, and "no error" clauses. Repeating a stated rule with a different input is the same rule,
not a new assertion. A parenthetical that explains why a stated result matters is not an assertion.
A step whose expected_result is only one of these gets `grounded: null`; it is neither grounded nor
a failure.

The case's scenario title may name another requirement; judge the steps, not the title. Judge only
the claimed requirement. Do not name a failure mode. Write the critique first, then the result.
"""


class StepCheck(BaseModel):
    step: int
    grounded: bool | None
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


def write_records(path: Path, records: Sequence[JudgeRecord]) -> None:
    write_rows(path, records)
