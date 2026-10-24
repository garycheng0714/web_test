import argparse
import os
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from web_test.automation.case_file import CaseFile
from web_test.automation.coding_agent import AutomationResult, create_automation
from web_test.automation.evidence import (
    AutomationEvidence,
    collect_traces,
    render_summary,
    write_evidence,
)
from web_test.automation.quality import QualityFinding, quality_findings
from web_test.automation.repair_guard import AutomationDeps
from web_test.automation.report import (
    RunReport,
    build_run_report,
    read_junit,
    render_run_report,
)
from web_test.command import CommandResult, subprocess_runner
from web_test.naming import run_token
from web_test.observability import configure_observability
from web_test.publishing.git import Git
from web_test.publishing.github import GitHubAdapter
from web_test.publishing.publish import Publisher
from web_test.publishing.suite import JUNIT_XML, Suite
from web_test.write_guard import allowed_paths


class AutomationStatus(StrEnum):
    PUBLISHED = "published"
    AGENT_RED = "agent_red"
    QUALITY_RED = "quality_red"
    SUITE_RED = "suite_red"
    NO_CHANGES = "no_changes"
    FAILED = "failed"


def exit_code(status: AutomationStatus) -> int:
    """Red outcomes fail the job so a silent run is visible; the gate is unchanged."""
    return 0 if status in (AutomationStatus.PUBLISHED, AutomationStatus.NO_CHANGES) else 1


@dataclass(frozen=True)
class AutomationOutcome:
    """How an automation run ended, with a failure reason and red-run evidence."""

    status: AutomationStatus
    error: str | None = None
    evidence: AutomationEvidence | None = field(default=None, compare=False)


def _generated_files(git: Git) -> list[str]:
    """Best-effort: evidence must never change the gate."""
    try:
        return allowed_paths(git.changed_paths())
    except (OSError, RuntimeError):
        return []


def _outcome(
    status: AutomationStatus,
    deps: AutomationDeps,
    suite: CommandResult | None,
    files: list[str],
    workspace: Path,
    *,
    error: str | None = None,
    quality: tuple[QualityFinding, ...] = (),
    report: RunReport | None = None,
) -> AutomationOutcome:
    traces, traces_skipped = collect_traces(workspace)
    return AutomationOutcome(
        status=status,
        error=error,
        evidence=AutomationEvidence(
            pytest_output=deps.last_pytest_output,
            pytest_runs=deps.pytest_runs,
            suite=suite,
            files=tuple(files),
            quality=quality,
            report=report,
            trace=tuple(deps.tool_trace),
            traces=traces,
            traces_skipped=traces_skipped,
        ),
    )


def _run_suite(
    suite: Suite, workspace: Path, files: Sequence[str]
) -> tuple[CommandResult, RunReport]:
    """Run the suite and read its JUnit results."""
    result = suite.run()
    report = build_run_report(read_junit(workspace / JUNIT_XML), files)
    return result, report


def _publish(
    case_id: str,
    pr_body: str,
    report: RunReport,
    files: list[str],
    *,
    git: Git,
    pr: GitHubAdapter,
    token: str | None,
) -> None:
    """Append the run report to the PR body and publish."""
    Publisher(git=git, pr=pr).publish(
        case_id=case_id,
        body=f"{pr_body}\n\n{render_run_report(report)}",
        files=files,
        token=token or run_token(),
    )


def automate(
    case_path: str | Path,
    *,
    workspace: str | Path,
    agent: Callable[..., AutomationResult] = create_automation,
    git: Git,
    pr: GitHubAdapter,
    suite: Suite,
    token: str | None = None,
) -> AutomationOutcome:
    """Implement the tests for one merged test-case artifact, and publish when green."""
    workspace = Path(workspace)
    deps = AutomationDeps()
    suite_result: CommandResult | None = None
    files: list[str] = []
    report: RunReport | None = None
    try:
        case, text = CaseFile.from_path(case_path)
        result = agent(text, workspace_dir=workspace, deps=deps)
        files = _generated_files(git)
        pr_body = result.pr_body

        if pr_body is None:
            return _outcome(AutomationStatus.AGENT_RED, deps, suite_result, files, workspace)

        quality = quality_findings(case.id, text, files, workspace)
        if quality:
            return _outcome(
                AutomationStatus.QUALITY_RED,
                deps,
                suite_result,
                files,
                workspace,
                quality=quality,
            )

        suite_result, report = _run_suite(suite, workspace, files)
        if suite_result.returncode != 0:
            return _outcome(
                AutomationStatus.SUITE_RED,
                deps,
                suite_result,
                files,
                workspace,
                report=report,
            )

        if not files:
            return _outcome(
                AutomationStatus.NO_CHANGES,
                deps,
                suite_result,
                files,
                workspace,
                report=report,
            )

        _publish(case.id, pr_body, report, files, git=git, pr=pr, token=token)
    except (RuntimeError, ValueError, OSError) as error:
        return _outcome(
            AutomationStatus.FAILED,
            deps,
            suite_result,
            files,
            workspace,
            error=str(error),
            report=report,
        )

    return _outcome(
        AutomationStatus.PUBLISHED,
        deps,
        suite_result,
        files,
        workspace,
        report=report,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="automate", description="Turn a merged test case into a PR.")
    parser.add_argument("--case", required=True, help="path to test-case/<id>.md")
    parser.add_argument("--workspace", default=".", help="repository the agent reads and edits")
    args = parser.parse_args(argv)

    configure_observability()
    workspace = Path(args.workspace)
    outcome = automate(
        args.case,
        workspace=workspace,
        git=Git(subprocess_runner, workspace),
        pr=GitHubAdapter.from_env(),
        suite=Suite(subprocess_runner, workspace),
    )

    summary = render_summary(outcome.status.value, outcome.error, outcome.evidence)
    evidence_dir = os.environ.get("WEB_TEST_EVIDENCE_DIR")
    if evidence_dir:
        try:
            summary = write_evidence(
                status=outcome.status.value,
                error=outcome.error,
                evidence=outcome.evidence,
                workspace=workspace,
                directory=Path(evidence_dir),
            )
        except OSError as error:
            print(f"evidence write failed: {error}", file=sys.stderr)

    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        try:
            with Path(step_summary).open("a", encoding="utf-8") as handle:
                handle.write(summary + "\n")
        except OSError as error:
            print(f"step summary write failed: {error}", file=sys.stderr)

    if outcome.status is AutomationStatus.FAILED:
        print(f"failed: {outcome.error}", file=sys.stderr)
    else:
        print(outcome.status.value)
    return exit_code(outcome.status)


if __name__ == "__main__":
    raise SystemExit(main())
