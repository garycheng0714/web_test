from dataclasses import dataclass

from web_test.planning.review.verification import (
    CheckDimension,
    CheckOutcome,
    VerificationStatus,
)


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
