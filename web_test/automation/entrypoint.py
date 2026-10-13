import argparse
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import HttpUrl

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


@dataclass(frozen=True)
class AutomationOutcome:
    """How an automation run ended, and the opened PR's URL when there is one."""

    status: AutomationStatus
    pr_url: HttpUrl | None = None


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

    if not suite.is_green():
        return AutomationOutcome(AutomationStatus.SUITE_RED)

    files = allowed_paths(git.changed_paths())
    if not files:
        return AutomationOutcome(AutomationStatus.NO_CHANGES)

    pr_url = Publisher(git=git, pr=pr).publish(case_id=case.id, body=result.pr_body, files=files)

    return AutomationOutcome(AutomationStatus.PUBLISHED, pr_url=pr_url)


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
    print(outcome.pr_url or outcome.status.value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
