import argparse
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from web_test.planning.review.jev import SystemOne, typesafe_system_one
from web_test.planning.review.questions import (
    STEP_QUALITY_DIMENSIONS,
    ac_id,
    case_key,
    step_id,
)
from web_test.planning.review.service import run_review_on
from web_test.planning.review.subject import ReviewCase, ReviewStep, ReviewSubject
from web_test.planning.review.verification import (
    CheckDimension,
    CheckOutcome,
    VerificationStatus,
)


class EvalStep(BaseModel):
    action: str
    expected_result: str


class EvalCase(BaseModel):
    id: str
    label: Literal["good", "bad"]
    tests: str | None = None
    requirement_ids: list[str]
    scenario: str
    preconditions: list[str] = []
    steps: list[EvalStep]


class ExpectedFailure(BaseModel):
    case: str
    dimension: CheckDimension
    step: int | None = None


class KillCriteria(BaseModel):
    caught_min: int = 0
    hard_fail_min: int = 0
    good_false_flags_max: int = 0
    bad_blocked_max: int = 0
    require_each_dimension: bool = True


class EvalSet(BaseModel):
    prd: str
    cases: list[EvalCase]
    expected_failures: list[ExpectedFailure]
    kill_criteria: KillCriteria


@dataclass(frozen=True)
class ExpectedCheckResult:
    question_id: str
    dimension: CheckDimension
    status: VerificationStatus
    probability: float | None


@dataclass(frozen=True)
class CaseEvaluation:
    case_id: str
    label: str
    tests: str | None
    scenario: str
    status: VerificationStatus
    expected: tuple[ExpectedCheckResult, ...]
    false_flags: tuple[CheckOutcome, ...]


@dataclass(frozen=True)
class DimensionTally:
    dimension: CheckDimension
    expected: int
    caught: int
    hard_fail: int
    false_flags: int


@dataclass(frozen=True)
class EvalReport:
    model: str
    question_set_version: str
    record_status: VerificationStatus
    cases: tuple[CaseEvaluation, ...]
    dimensions: tuple[DimensionTally, ...]
    caught: int
    expected: int
    hard_fail: int
    blocked: int
    needs_review_cases: int
    needs_review_rate: float
    good_false_flags: int
    override_rate: float | None
    criteria: tuple[tuple[str, bool], ...]
    kill_criteria_passed: bool
    runs: int = 1
    reproduced: bool | None = None


def load_eval_set(path: str | Path) -> EvalSet:
    return EvalSet.model_validate_json(Path(path).read_text(encoding="utf-8"))


def _subject(eval_set: EvalSet) -> ReviewSubject:
    return ReviewSubject(
        prd=eval_set.prd,
        cases=[
            ReviewCase(
                index=index,
                requirement_ids=case.requirement_ids,
                module_feature="",
                test_scenario=case.scenario,
                preconditions=case.preconditions,
                steps=[
                    ReviewStep(
                        index=step_index,
                        action=step.action,
                        expected_result=step.expected_result,
                    )
                    for step_index, step in enumerate(case.steps, start=1)
                ],
            )
            for index, case in enumerate(eval_set.cases, start=1)
        ],
    )


def _case_checks(case: ReviewCase) -> list[str]:
    ids = [ac_id(case.index)]
    for step in case.steps:
        ids.extend(
            step_id(case.index, step.index, dimension)
            for dimension in STEP_QUALITY_DIMENSIONS
        )
    return ids


def _check_result(
    question_id: str,
    dimension: CheckDimension,
    by_id: dict[str, CheckOutcome],
) -> ExpectedCheckResult:
    check = by_id.get(question_id)
    return ExpectedCheckResult(
        question_id=question_id,
        dimension=dimension,
        status=check.status if check is not None else VerificationStatus.BLOCKED,
        probability=check.probability if check is not None else None,
    )


def evaluate(
    eval_set: EvalSet,
    *,
    system_one: SystemOne,
) -> EvalReport:
    subject = _subject(eval_set)
    record = run_review_on(
        subject,
        eval_set.model_dump_json(),
        system_one=system_one,
    )
    checks = {check.question_id: check for check in record.result.checks}
    case_status = {case.key: case.status for case in record.result.cases}
    case_results = []
    for index, eval_case in enumerate(eval_set.cases, start=1):
        review_case = subject.cases[index - 1]
        expected = []
        for failure in eval_set.expected_failures:
            if failure.case != eval_case.id:
                continue
            question_id = (
                ac_id(index)
                if failure.step is None
                else step_id(index, failure.step, failure.dimension)
            )
            expected.append(_check_result(question_id, failure.dimension, checks))

        false_flags = ()
        if eval_case.label == "good":
            false_flags = tuple(
                checks[question_id]
                for question_id in _case_checks(review_case)
                if checks[question_id].status is not VerificationStatus.PASS
            )

        case_results.append(
            CaseEvaluation(
                case_id=eval_case.id,
                label=eval_case.label,
                tests=eval_case.tests,
                scenario=eval_case.scenario,
                status=case_status[case_key(index)],
                expected=tuple(expected),
                false_flags=false_flags,
            )
        )

    expected_results = [
        result for case in case_results if case.label == "bad" for result in case.expected
    ]
    caught = sum(
        result.status in {VerificationStatus.FAIL, VerificationStatus.NEEDS_REVIEW}
        for result in expected_results
    )
    hard_fail = sum(result.status is VerificationStatus.FAIL for result in expected_results)
    blocked = sum(result.status is VerificationStatus.BLOCKED for result in expected_results)
    good_false_flags = sum(len(case.false_flags) for case in case_results if case.label == "good")
    needs_review_cases = sum(
        case.status is VerificationStatus.NEEDS_REVIEW for case in case_results
    )

    dimensions = []
    for dimension in CheckDimension:
        expected_for_dimension = [
            result for result in expected_results if result.dimension is dimension
        ]
        false_flags_for_dimension = sum(
            1
            for case in case_results
            if case.label == "good"
            for check in case.false_flags
            if check.dimension is dimension
        )
        dimensions.append(
            DimensionTally(
                dimension=dimension,
                expected=len(expected_for_dimension),
                caught=sum(
                    result.status
                    in {VerificationStatus.FAIL, VerificationStatus.NEEDS_REVIEW}
                    for result in expected_for_dimension
                ),
                hard_fail=sum(
                    result.status is VerificationStatus.FAIL
                    for result in expected_for_dimension
                ),
                false_flags=false_flags_for_dimension,
            )
        )

    criteria = (
        ("caught", caught >= eval_set.kill_criteria.caught_min),
        ("hard_fail", hard_fail >= eval_set.kill_criteria.hard_fail_min),
        (
            "good_false_flags",
            good_false_flags <= eval_set.kill_criteria.good_false_flags_max,
        ),
        ("bad_blocked", blocked <= eval_set.kill_criteria.bad_blocked_max),
        (
            "each_dimension",
            not eval_set.kill_criteria.require_each_dimension
            or all(dimension.expected > 0 for dimension in dimensions),
        ),
    )

    return EvalReport(
        model=record.binding.model,
        question_set_version=record.binding.question_set_version,
        record_status=record.result.status,
        cases=tuple(case_results),
        dimensions=tuple(dimensions),
        caught=caught,
        expected=len(expected_results),
        hard_fail=hard_fail,
        blocked=blocked,
        needs_review_cases=needs_review_cases,
        needs_review_rate=needs_review_cases / len(case_results) if case_results else 0.0,
        good_false_flags=good_false_flags,
        override_rate=None,
        criteria=criteria,
        kill_criteria_passed=all(passed for _, passed in criteria),
    )


def _signature(report: EvalReport) -> tuple[object, ...]:
    return (
        tuple((case.case_id, case.status) for case in report.cases),
        tuple(
            (case.case_id, tuple(check.question_id for check in case.false_flags))
            for case in report.cases
        ),
        tuple(
            (case.case_id, tuple((result.question_id, result.status) for result in case.expected))
            for case in report.cases
            if case.label == "bad"
        ),
    )


def _text(value: str) -> str:
    return " ".join(value.split())


def _p(value: float | None) -> str:
    return "n/a" if value is None else str(round(value, 2))


def render_eval_report(report: EvalReport) -> str:
    run_note = (
        "directional, one run"
        if report.runs == 1
        else ("reproduced" if report.reproduced else "unstable across runs")
    )
    criteria = "\n".join(
        f"- {name}: {'PASS' if passed else 'FAIL'}" for name, passed in report.criteria
    )

    lines = [
        "## Review eval",
        "",
        f"**Model:** `{report.model}`",
        f"**Question set:** `{report.question_set_version}`",
        f"**Runs:** {report.runs} ({run_note})",
        f"**Record status:** `{report.record_status.value}`",
        f"**Needs review rate:** {report.needs_review_cases}/{len(report.cases)} cases "
        f"({report.needs_review_rate:.0%})",
        "**Override rate:** n/a (until ticket 24b)",
        f"**Kill criteria:** {'PASS' if report.kill_criteria_passed else 'FAIL'}",
        "",
        criteria,
        "",
        "### Bad cases",
        "",
        "| Case | Tests | Expected | Status | p | Caught | Hard fail |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for case in report.cases:
        if case.label != "bad":
            continue
        for result in case.expected:
            caught = result.status in {
                VerificationStatus.FAIL,
                VerificationStatus.NEEDS_REVIEW,
            }
            lines.append(
                f"| {case.case_id} | {_text(case.tests or case.scenario)} | "
                f"{result.dimension} ({result.question_id}) | `{result.status.value}` | "
                f"{_p(result.probability)} | {'yes' if caught else 'no'} | "
                f"{'yes' if result.status is VerificationStatus.FAIL else 'no'} |"
            )

    lines += ["", "### Good cases", "", "| Case | False flags |", "| --- | --- |"]
    for case in report.cases:
        if case.label != "good":
            continue
        flags = (
            ", ".join(
                f"{_text(check.label)} ({check.dimension}, p={_p(check.probability)})"
                for check in case.false_flags
            )
            or "None."
        )
        lines.append(f"| {case.case_id} | {flags} |")

    lines += [
        "",
        "### Per dimension",
        "",
        "| Dimension | Bad variants | Caught | Hard fail | False flags |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for dimension in report.dimensions:
        status = "inconclusive" if dimension.expected == 0 else str(dimension.caught)
        lines.append(
            f"| {dimension.dimension} | {dimension.expected} | {status} | "
            f"{dimension.hard_fail} | {dimension.false_flags} |"
        )

    lines += [
        "",
        "### Limits",
        "",
        "- One run is directional, not a stable estimate."
        if report.runs == 1
        else "- Multiple runs only show stability for this fixture set; it is not statistical confidence.",
        "- Override rate is unavailable until ticket 24b implements human adjudication.",
        "- BLOCKED means no answer, not a caught defect.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="review-eval", description="Evaluate the Jev verifier.")
    parser.add_argument(
        "--fixtures",
        default="tests/fixtures/review_eval/register_login_golden_v1.json",
        help="path to the eval fixture JSON",
    )
    parser.add_argument("--runs", type=int, default=1, help="number of runs (default: 1)")
    args = parser.parse_args(argv)
    if args.runs < 1:
        print("failed: --runs must be at least 1", file=sys.stderr)
        return 1

    try:
        eval_set = load_eval_set(args.fixtures)
        reports = [
            evaluate(eval_set, system_one=typesafe_system_one)
            for _ in range(args.runs)
        ]
    except (OSError, ValueError) as error:
        print(f"failed: {error}", file=sys.stderr)
        return 1

    report = reports[0]
    if len(reports) > 1:
        first = _signature(report)
        report = replace(
            report,
            runs=len(reports),
            reproduced=all(_signature(item) == first for item in reports[1:]),
        )

    print(render_eval_report(report))
    return 0 if report.kill_criteria_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
