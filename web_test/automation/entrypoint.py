import argparse
from collections.abc import Callable
from pathlib import Path

import yaml
from pydantic import BaseModel, HttpUrl

from web_test.automation.coding_agent import AutomationResult, create_automation
from web_test.command import subprocess_runner
from web_test.planning.schema import CaseType, Priority
from web_test.publishing.git import Git
from web_test.publishing.github import GitHub
from web_test.publishing.publish import Publisher, allowed_paths
from web_test.publishing.suite import Suite


class CaseFile(BaseModel):
    """The machine-readable front-matter of a merged test-case artifact."""

    id: str
    base_url: HttpUrl
    requirement_ids: list[str] = []
    priority: Priority = Priority.MEDIUM
    test_type: CaseType = CaseType.FUNCTIONAL


def _front_matter(text: str) -> dict[str, object]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return yaml.safe_load("\n".join(lines[1:index])) or {}
    return {}


def parse_case(text: str) -> CaseFile:
    return CaseFile.model_validate(_front_matter(text))


def _validate_case_path(path: Path) -> None:
    if path.parent.name != "test-case" or not path.name.startswith("test-case-") or path.suffix != ".md":
        raise ValueError(f"{path} is not a test-case artifact (expected test-case/<id>.md).")


def automate(
    case_path: str | Path,
    *,
    workspace: str | Path,
    agent: Callable[..., AutomationResult] = create_automation,
    git: Git,
    pr: GitHub,
    suite: Suite,
) -> HttpUrl | None:
    """Implement the tests for one merged test-case artifact and open a PR when green.

    Returns the opened PR's URL, else `None` (the agent reported a red suite, the
    suite is red, or nothing permitted changed).
    """
    path = Path(case_path)
    _validate_case_path(path)
    text = path.read_text(encoding="utf-8")
    case = parse_case(text)
    result = agent(text, workspace_dir=workspace)
    if result.pr_body is None:
        return None
    if not suite.is_green():
        return None
    files = allowed_paths(git.changed_paths())
    if not files:
        return None
    return Publisher(git=git, pr=pr).publish(case_id=case.id, body=result.pr_body, files=files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="automate", description="Turn a merged test case into a PR.")
    parser.add_argument("--case", required=True, help="path to test-case/<id>.md")
    parser.add_argument("--workspace", default=".", help="repository the agent reads and edits")
    args = parser.parse_args(argv)

    workspace = Path(args.workspace)
    pr_url = automate(
        args.case,
        workspace=workspace,
        git=Git(subprocess_runner, workspace),
        pr=GitHub(subprocess_runner, workspace),
        suite=Suite(subprocess_runner, workspace),
    )
    print(pr_url or "no PR created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
