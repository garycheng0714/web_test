import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import ValidationError

from web_test.automation.case_file import CaseFile
from web_test.automation.coding_agent import AutomationResult, create_automation
from web_test.command import subprocess_runner
from web_test.publishing.git import Git
from web_test.publishing.github import GitHub
from web_test.publishing.publish import Publisher
from web_test.publishing.suite import Suite
from web_test.write_guard import allowed_paths


class AutomationStatus(StrEnum):
    PUBLISHED = "published"
    AGENT_RED = "agent_red"
    SUITE_RED = "suite_red"
    NO_CHANGES = "no_changes"
    FAILED = "failed"


@dataclass(frozen=True)
class AutomationOutcome:
    """How an automation run ended, with a failure reason when there is one."""

    status: AutomationStatus
    error: str | None = None


def automate(
    case_path: str | Path,
    *,
    workspace: str | Path,
    agent: Callable[..., AutomationResult] = create_automation,
    git: Git,
    pr: GitHub,
    suite: Suite,
) -> AutomationOutcome:
    """Implement the tests for one merged test-case artifact, and publish when green."""
    case, text = CaseFile.from_path(case_path)
    result = agent(text, workspace_dir=workspace)

    if result.pr_body is None:
        return AutomationOutcome(AutomationStatus.AGENT_RED)

    try:
        if not suite.is_green():
            return AutomationOutcome(AutomationStatus.SUITE_RED)

        files = allowed_paths(git.changed_paths())
        if not files:
            return AutomationOutcome(AutomationStatus.NO_CHANGES)

        Publisher(git=git, pr=pr).publish(case_id=case.id, body=result.pr_body, files=files)
    except (RuntimeError, ValidationError, OSError) as error:
        return AutomationOutcome(AutomationStatus.FAILED, error=str(error))

    return AutomationOutcome(AutomationStatus.PUBLISHED)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="automate", description="Turn a merged test case into a PR.")
    parser.add_argument("--case", required=True, help="path to test-case/<id>.md")
    parser.add_argument("--workspace", default=".", help="repository the agent reads and edits")
    args = parser.parse_args(argv)

    workspace = Path(args.workspace)
    outcome = automate(
        args.case,
        workspace=workspace,
        git=Git(subprocess_runner, workspace),
        pr=GitHub(subprocess_runner, workspace),
        suite=Suite(subprocess_runner, workspace),
    )
    if outcome.status is AutomationStatus.FAILED:
        print(f"failed: {outcome.error}", file=sys.stderr)
        return 1
    print(outcome.status.value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
