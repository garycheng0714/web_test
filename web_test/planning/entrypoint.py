import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path

from pydantic import ValidationError

from web_test.command import subprocess_runner
from web_test.observability import configure_observability
from web_test.planning.cases_writer import CaseWriter
from web_test.planning.designer import design_test_cases
from web_test.planning.publisher import TEST_CASE_DIR, PlanPublisher
from web_test.planning.schema import Case
from web_test.publishing.git import Git
from web_test.publishing.github import GitHub


class PlanStatus(StrEnum):
    PLANNED = "planned"
    NO_CASES = "no_cases"
    FAILED = "failed"


@dataclass(frozen=True)
class PlanOutcome:
    """How a plan run ended, with the files it added and a failure reason when there is one."""

    status: PlanStatus
    files: list[str] = field(default_factory=list)
    error: str | None = None


def plan_branch(prd_stem: str, now: datetime) -> str:
    return f"plan/{prd_stem}-{now.astimezone(timezone.utc):%Y%m%dT%H%M%SZ}"


def commit_message(prd_name: str) -> str:
    return f"Add test cases from {prd_name}"


def plan(
    prd_path: str | Path,
    *,
    base_url: str,
    workspace: str | Path,
    agent: Callable[..., list[Case]] = design_test_cases,
    git: Git,
    pr: GitHub,
    now: datetime | None = None,
) -> PlanOutcome:
    """Turn one PRD into a PR that adds one `test-case/<prd-stem>.md` file."""
    prd = Path(prd_path)
    workspace = Path(workspace)
    try:
        cases = agent(prd.read_text(encoding="utf-8"))
        if not cases:
            return PlanOutcome(PlanStatus.NO_CASES)

        publisher = PlanPublisher(
            git=git, pr=pr, writer=CaseWriter(workspace / TEST_CASE_DIR, base_url=base_url)
        )

        files = publisher.publish(
            branch=plan_branch(prd.stem, now or datetime.now(timezone.utc)),
            message=commit_message(prd.name),
            prd_stem=prd.stem,
            cases=cases,
        )
    except (RuntimeError, ValidationError, OSError) as error:
        return PlanOutcome(PlanStatus.FAILED, error=str(error))

    return PlanOutcome(PlanStatus.PLANNED, files=files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="plan", description="Turn a PRD into a test-case PR.")
    parser.add_argument("--prd", required=True, help="path to the PRD markdown/text file")
    parser.add_argument("--base-url", required=True, help="base URL for the test-case front-matter")
    parser.add_argument("--workspace", default=".", help="repository the plan writes into")
    args = parser.parse_args(argv)

    configure_observability()
    workspace = Path(args.workspace)
    outcome = plan(
        args.prd,
        base_url=args.base_url,
        workspace=workspace,
        git=Git(subprocess_runner, workspace),
        pr=GitHub(subprocess_runner, workspace),
    )
    if outcome.status is PlanStatus.FAILED:
        print(f"failed: {outcome.error}", file=sys.stderr)
        return 1
    if outcome.status is PlanStatus.NO_CASES:
        print("no test cases were produced", file=sys.stderr)
        return 1
    print(outcome.status.value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
