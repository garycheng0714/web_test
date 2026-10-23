import argparse
import os
import sys
from collections.abc import Callable, Iterable
from pathlib import Path

from pydantic import BaseModel

from web_test.planning.review.jev import SystemOne, typesafe_system_one
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.report import render_report
from web_test.planning.review.service import run_review_on
from web_test.planning.review.verification import VerificationStatus
from web_test.planning.verify_cache import VerdictCache
from web_test.planning.verify_payload import early_payload, verdict_payload
from web_test.planning.verify_resolution import ResolutionKind, resolve
from web_test.publishing.github import CheckPayload, GitHubAdapter


class VerificationInputFile(BaseModel):
    """The verification input file `prepare` writes and `run` reads."""

    kind: ResolutionKind
    files: list[str] = []
    detail: str = ""
    test_case_text: str | None = None
    prd_text: str | None = None
    cache_key: str | None = None


def prepare(
    changed_paths: Iterable[str], *, workspace: Path
) -> VerificationInputFile:
    """Resolve the changed paths to the verification input."""
    resolution = resolve(changed_paths, workspace=workspace)
    verdict_input = resolution.verdict_input
    return VerificationInputFile(
        kind=resolution.kind,
        files=list(resolution.files),
        detail=resolution.detail,
        test_case_text=verdict_input.test_case.text if verdict_input else None,
        prd_text=verdict_input.prd.text if verdict_input else None,
        cache_key=verdict_input.cache_key if verdict_input else None,
    )


def run(
    verification_file: VerificationInputFile,
    *,
    head_sha: str,
    publish: Callable[[CheckPayload], None],
    name: str = "verify-test-case",
    system_one: SystemOne = typesafe_system_one,
    cache: VerdictCache | None = None,
) -> CheckPayload:
    """Publish the check for the verification input: an early outcome, or the verdict."""
    if (
        cache is not None
        and verification_file.kind is ResolutionKind.READY
        and verification_file.cache_key is not None
    ):
        cached = cache.load(verification_file.cache_key)
        if cached is not None:
            payload = cached.model_copy(update={"head_sha": head_sha, "name": name})
            publish(payload)
            return payload

    cacheable = False
    if verification_file.kind is not ResolutionKind.READY:
        payload = early_payload(
            verification_file.kind,
            head_sha=head_sha,
            name=name,
            files=verification_file.files,
            detail=verification_file.detail,
        )
    else:
        if (
            verification_file.test_case_text is None
            or verification_file.prd_text is None
            or verification_file.cache_key is None
        ):
            raise ValueError(
                "ready verification input is missing its verdict data"
            )
        subject = parse_test_case(
            verification_file.test_case_text, verification_file.prd_text
        )
        record = run_review_on(
            subject, verification_file.test_case_text, system_one=system_one
        )
        cacheable = record.result.status is not VerificationStatus.BLOCKED
        payload = verdict_payload(
            record.result.status,
            summary=render_report(record),
            head_sha=head_sha,
            name=name,
            external_id=verification_file.cache_key,
        )
    publish(payload)
    if cache is not None and cacheable:
        cache.save(payload)
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
    prepare_parser.add_argument("--verification-input", required=True)
    prepare_parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))

    run_parser = subcommands.add_parser("run")
    run_parser.add_argument("--verification-input", required=True)
    run_parser.add_argument("--head-sha", required=True)
    run_parser.add_argument("--check-name", default="verify-test-case")
    run_parser.add_argument("--cache-dir")
    run_parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))

    args = parser.parse_args(argv)

    if args.command == "prepare":
        try:
            changed = _read_changed_files(Path(args.changed_files))
            verification_input = prepare(changed, workspace=Path(args.workspace))
            input_path = Path(args.verification_input)
            input_path.parent.mkdir(parents=True, exist_ok=True)
            input_path.write_text(
                verification_input.model_dump_json(indent=2) + "\n",
                encoding="utf-8",
            )
            key = verification_input.cache_key or ""
            _write_output(
                Path(args.github_output) if args.github_output else None,
                [f"key={key}"],
            )
        except (OSError, ValueError) as error:
            print(f"failed: {error}", file=sys.stderr)
            return 1
        return 0

    try:
        verification_input = VerificationInputFile.model_validate_json(
            Path(args.verification_input).read_text(encoding="utf-8")
        )
        cache = VerdictCache(Path(args.cache_dir)) if args.cache_dir else None
        payload = run(
            verification_input,
            head_sha=args.head_sha,
            name=args.check_name,
            publish=GitHubAdapter.from_env().publish_check,
            cache=cache,
        )
        if cache is not None:
            _write_output(
                Path(args.github_output) if args.github_output else None,
                [f"saved={'true' if cache.saved else 'false'}"],
            )
    except (OSError, ValueError, RuntimeError) as error:
        print(f"failed: {error}", file=sys.stderr)
        return 1

    print(f"published {payload.name}: {payload.conclusion}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
