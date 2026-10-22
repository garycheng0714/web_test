import argparse
import os
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel

from web_test.planning.review.jev import JEV_MODEL, SystemOne, typesafe_system_one
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.questions import (
    question_set_version,
    questions_for_subject,
)
from web_test.planning.review.record import DEFAULT_BANDS
from web_test.planning.review.report import render_report
from web_test.planning.review.service import run_review_on
from web_test.planning.review.verification import (
    VerificationRecord,
    VerificationStatus,
    digest_text,
)
from web_test.publishing.github import (
    CheckConclusion,
    CheckPayload,
    GitHubAdapter,
    GitHubError,
)


class ResolutionKind(StrEnum):
    """How resolving the changed paths ended."""

    READY = "ready"
    NOTHING = "nothing"
    MULTIPLE = "multiple"
    MISSING_PRD = "missing_prd"
    INVALID = "invalid"


@dataclass(frozen=True)
class CheckInput:
    """The exact artifact, PRD, and configuration a verdict is bound to."""

    case_path: Path
    prd_path: Path
    test_case_text: str
    prd_text: str
    test_case_digest: str
    prd_digest: str
    question_set_version: str
    cache_key: str


@dataclass(frozen=True)
class Resolution:
    """The result of resolving the changed paths."""

    kind: ResolutionKind
    files: tuple[str, ...] = ()
    detail: str = ""
    check_input: CheckInput | None = None


class PlanInput(BaseModel):
    """The check input stored in the plan file."""

    case_path: Path
    prd_path: Path
    test_case_text: str
    prd_text: str
    test_case_digest: str
    prd_digest: str
    question_set_version: str
    cache_key: str


class Plan(BaseModel):
    """The plan file `prepare` writes and `run` reads."""

    kind: ResolutionKind
    check_input: PlanInput | None = None
    files: list[str] = []
    detail: str = ""


# shortcut: mirrors automation.case_file's artifact shape; share if a third caller appears.
def _is_artifact(path: Path) -> bool:
    return (
        path.parent.name == "test-case"
        and path.name.startswith("test-case-")
        and path.suffix == ".md"
    )


def _front_matter_id(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing front matter")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            break
    else:
        raise ValueError("unterminated front matter")
    data = yaml.safe_load("\n".join(lines[1:index])) or {}
    case_id = data.get("id") if isinstance(data, dict) else None
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("front matter needs a string id")
    return case_id


def _read_case(workspace: Path, case_path: Path) -> tuple[str, str]:
    case_file = case_path if case_path.is_absolute() else workspace / case_path
    text = case_file.read_text(encoding="utf-8")
    return text, _front_matter_id(text)


def _read_prd(workspace: Path, case_id: str) -> tuple[Path, str]:
    path = workspace / "prd" / f"{case_id}.md"
    if not path.is_file():
        raise FileNotFoundError(f"{path} does not exist")
    try:
        return path, path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"reading PRD {path} failed: {error}") from error


def _cache_key(test_case_digest: str, prd_digest: str, version: str) -> str:
    payload = "\n".join(
        [
            test_case_digest,
            prd_digest,
            version,
            JEV_MODEL,
            str(DEFAULT_BANDS.pass_min),
            str(DEFAULT_BANDS.needs_review_min),
        ]
    )
    return digest_text(payload)


def resolve(changed_paths: Iterable[str], *, workspace: Path) -> Resolution:
    """Resolve the changed paths to the single Test Case file and its inputs."""
    artifacts = sorted(
        path for path in (Path(raw) for raw in changed_paths) if _is_artifact(path)
    )
    if not artifacts:
        return Resolution(ResolutionKind.NOTHING)
    if len(artifacts) > 1:
        return Resolution(ResolutionKind.MULTIPLE, files=tuple(str(path) for path in artifacts))

    case_path = artifacts[0]
    try:
        test_case_text, case_id = _read_case(workspace, case_path)
    except (OSError, ValueError) as error:
        return Resolution(ResolutionKind.INVALID, detail=str(error))

    try:
        prd_path, prd_text = _read_prd(workspace, case_id)
    except FileNotFoundError as error:
        return Resolution(ResolutionKind.MISSING_PRD, detail=str(error))
    except ValueError as error:
        return Resolution(ResolutionKind.INVALID, detail=str(error))

    try:
        subject = parse_test_case(test_case_text, prd_text)
    except (ValueError, yaml.YAMLError) as error:
        return Resolution(ResolutionKind.INVALID, detail=str(error))

    version = question_set_version(questions_for_subject(subject))
    test_case_digest = digest_text(test_case_text)
    prd_digest = digest_text(prd_text)
    return Resolution(
        ResolutionKind.READY,
        check_input=CheckInput(
            case_path=case_path,
            prd_path=prd_path,
            test_case_text=test_case_text,
            prd_text=prd_text,
            test_case_digest=test_case_digest,
            prd_digest=prd_digest,
            question_set_version=version,
            cache_key=_cache_key(test_case_digest, prd_digest, version),
        ),
    )

def _plan_from_resolution(resolution: Resolution) -> Plan:
    check_input = resolution.check_input
    return Plan(
        kind=resolution.kind,
        files=list(resolution.files),
        detail=resolution.detail,
        check_input=None
        if check_input is None
        else PlanInput(
            case_path=check_input.case_path,
            prd_path=check_input.prd_path,
            test_case_text=check_input.test_case_text,
            prd_text=check_input.prd_text,
            test_case_digest=check_input.test_case_digest,
            prd_digest=check_input.prd_digest,
            question_set_version=check_input.question_set_version,
            cache_key=check_input.cache_key,
        ),
    )


def prepare(
    changed_paths: Iterable[str], *, workspace: Path, plan_path: Path
) -> Plan:
    """Resolve the changed paths and write the plan file."""
    plan = _plan_from_resolution(resolve(changed_paths, workspace=workspace))
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(plan.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return plan


_CONCLUSIONS: dict[VerificationStatus, CheckConclusion] = {
    VerificationStatus.PASS: "success",
    VerificationStatus.NEEDS_REVIEW: "action_required",
    VerificationStatus.FAIL: "failure",
    VerificationStatus.BLOCKED: "failure",
}


def _early_payload(plan: Plan, *, head_sha: str, name: str) -> CheckPayload:
    if plan.kind is ResolutionKind.NOTHING:
        return CheckPayload(
            name=name,
            head_sha=head_sha,
            conclusion="success",
            title="Test Case verification: no Test Case file",
            summary="This PR does not change a `test-case/test-case-*.md` file.",
            external_id="no-test-case",
        )
    if plan.kind is ResolutionKind.MULTIPLE:
        files = "\n".join(f"- `{path}`" for path in plan.files)
        return CheckPayload(
            name=name,
            head_sha=head_sha,
            conclusion="failure",
            title="Test Case verification: multiple Test Case files",
            summary=f"Exactly one Test Case file is supported per PR.\n\n{files}",
            external_id="multiple-test-cases",
        )
    if plan.kind is ResolutionKind.MISSING_PRD:
        return CheckPayload(
            name=name,
            head_sha=head_sha,
            conclusion="failure",
            title="Test Case verification: missing PRD",
            summary=f"The PRD was not found: `{plan.detail}`",
            external_id="missing-prd",
        )
    if plan.kind is ResolutionKind.INVALID:
        return CheckPayload(
            name=name,
            head_sha=head_sha,
            conclusion="failure",
            title="Test Case verification: invalid Test Case",
            summary=plan.detail or "The Test Case file could not be read.",
            external_id="invalid-test-case",
        )
    raise ValueError("a ready plan needs a review")


def _verdict_payload(
    record: VerificationRecord, *, head_sha: str, name: str, external_id: str
) -> CheckPayload:
    status = record.result.status
    return CheckPayload(
        name=name,
        head_sha=head_sha,
        conclusion=_CONCLUSIONS[status],
        title=f"Test Case verification: {status.value}",
        summary=render_report(record),
        external_id=external_id,
    )


def run(
    plan: Plan,
    *,
    head_sha: str,
    publish: Callable[[CheckPayload], None],
    name: str = "verify-test-case",
    system_one: SystemOne = typesafe_system_one,
) -> CheckPayload:
    """Publish the check for the plan: an early outcome, or the Jev verdict."""
    if plan.kind is not ResolutionKind.READY:
        payload = _early_payload(plan, head_sha=head_sha, name=name)
    else:
        if plan.check_input is None:
            raise ValueError("ready plan is missing its check input")
        check = plan.check_input
        subject = parse_test_case(check.test_case_text, check.prd_text)
        record = run_review_on(subject, check.test_case_text, system_one=system_one)
        payload = _verdict_payload(
            record,
            head_sha=head_sha,
            name=name,
            external_id=check.cache_key,
        )
    publish(payload)
    return payload


def _read_changed_files(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_output(path: Path | None, lines: list[str]) -> None:
    text = "\n".join(lines) + "\n"
    if path is None:
        print(text, end="")
    else:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="review-check", description="Publish the Test Case verification check."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subcommands.add_parser("prepare")
    prepare_parser.add_argument("--changed-files", required=True)
    prepare_parser.add_argument("--workspace", default=".")
    prepare_parser.add_argument("--plan", required=True)
    prepare_parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))

    run_parser = subcommands.add_parser("run")
    run_parser.add_argument("--plan", required=True)
    run_parser.add_argument("--head-sha", required=True)
    run_parser.add_argument("--check-name", default="verify-test-case")

    args = parser.parse_args(argv)

    if args.command == "prepare":
        try:
            changed = _read_changed_files(Path(args.changed_files))
            plan = prepare(
                changed,
                workspace=Path(args.workspace),
                plan_path=Path(args.plan),
            )
        except (OSError, ValueError) as error:
            print(f"failed: {error}", file=sys.stderr)
            return 1
        key = plan.check_input.cache_key if plan.check_input else ""
        _write_output(
            Path(args.github_output) if args.github_output else None,
            [f"key={key}"],
        )
        return 0

    try:
        plan = Plan.model_validate_json(Path(args.plan).read_text(encoding="utf-8"))
        payload = run(
            plan,
            head_sha=args.head_sha,
            name=args.check_name,
            publish=GitHubAdapter.from_env().publish_check,
        )
    except (OSError, ValueError, GitHubError) as error:
        print(f"failed: {error}", file=sys.stderr)
        return 1

    print(f"published {payload.name}: {payload.conclusion}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
