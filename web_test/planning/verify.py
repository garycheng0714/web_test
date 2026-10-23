import argparse
import os
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from web_test.planning.review.jev import SystemOne, typesafe_system_one
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.report import render_report
from web_test.planning.review.service import run_review_on
from web_test.planning.review.verification import VerificationStatus
from web_test.planning.verify_cache import VerdictCache
from web_test.planning.verify_key import InvalidTestCase, cache_key
from web_test.planning.verify_payload import early_payload, verdict_payload
from web_test.planning.verify_resolution import ResolutionKind, resolve
from web_test.publishing.github import CheckPayload, GitHubAdapter


class PreparedVerification(BaseModel):
    """The verification input file `prepare` writes and `run` reads."""

    kind: ResolutionKind
    files: list[str] = []
    detail: str = ""
    test_case_text: str | None = None
    prd_text: str | None = None
    cache_key: str | None = None


@dataclass(frozen=True)
class RunResult:
    """The published check and whether its verdict was written to the cache."""

    payload: CheckPayload
    saved: bool


def prepare(
    changed_paths: Iterable[str], *, workspace: Path
) -> PreparedVerification:
    """Resolve the changed paths to the verification input."""
    resolution = resolve(changed_paths, workspace=workspace)
    if resolution.kind is not ResolutionKind.READY:
        return PreparedVerification(
            kind=resolution.kind,
            files=list(resolution.files),
            detail=resolution.detail,
        )

    texts = resolution.texts
    if texts is None:
        raise ValueError("ready resolution is missing its texts")
    try:
        key = cache_key(texts.test_case_text, texts.prd_text)
    except InvalidTestCase as error:
        return PreparedVerification(kind=ResolutionKind.INVALID, detail=str(error))
    return PreparedVerification(
        kind=ResolutionKind.READY,
        test_case_text=texts.test_case_text,
        prd_text=texts.prd_text,
        cache_key=key,
    )


def run(
    prepared_verification: PreparedVerification,
    *,
    head_sha: str,
    publish: Callable[[CheckPayload], None],
    name: str = "verify-test-case",
    system_one: SystemOne = typesafe_system_one,
    cache: VerdictCache | None = None,
) -> RunResult:
    """Publish the check for the verification input: an early outcome, or the verdict."""
    if prepared_verification.kind is not ResolutionKind.READY:
        payload = early_payload(
            prepared_verification.kind,
            head_sha=head_sha,
            name=name,
            files=prepared_verification.files,
            detail=prepared_verification.detail,
        )
        publish(payload)
        return RunResult(payload=payload, saved=False)

    test_case_text = prepared_verification.test_case_text
    prd_text = prepared_verification.prd_text
    cache_key = prepared_verification.cache_key
    if test_case_text is None or prd_text is None or cache_key is None:
        raise ValueError("ready verification input is missing its verdict data")

    if cache is not None:
        cached = cache.load(cache_key)
        if cached is not None:
            payload = cached.model_copy(update={"head_sha": head_sha, "name": name})
            publish(payload)
            return RunResult(payload=payload, saved=False)

    subject = parse_test_case(test_case_text, prd_text)
    record = run_review_on(subject, test_case_text, system_one=system_one)
    payload = verdict_payload(
        record.result.status,
        summary=render_report(record),
        head_sha=head_sha,
        name=name,
        external_id=cache_key,
    )
    publish(payload)
    saved = False
    if cache is not None and record.result.status is not VerificationStatus.BLOCKED:
        cache.save(payload)
        saved = True
    return RunResult(payload=payload, saved=saved)


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
            prepared_verification = prepare(changed, workspace=Path(args.workspace))
            input_path = Path(args.verification_input)
            input_path.parent.mkdir(parents=True, exist_ok=True)
            input_path.write_text(
                prepared_verification.model_dump_json(indent=2) + "\n",
                encoding="utf-8",
            )
            key = prepared_verification.cache_key or ""
            _write_output(
                Path(args.github_output) if args.github_output else None,
                [f"key={key}"],
            )
        except (OSError, ValueError) as error:
            print(f"failed: {error}", file=sys.stderr)
            return 1
        return 0

    try:
        prepared_verification = PreparedVerification.model_validate_json(
            Path(args.verification_input).read_text(encoding="utf-8")
        )
        cache = VerdictCache(Path(args.cache_dir)) if args.cache_dir else None
        result = run(
            prepared_verification,
            head_sha=args.head_sha,
            name=args.check_name,
            publish=GitHubAdapter.from_env().publish_check,
            cache=cache,
        )
        if cache is not None:
            _write_output(
                Path(args.github_output) if args.github_output else None,
                [f"saved={'true' if result.saved else 'false'}"],
            )
    except (OSError, ValueError, RuntimeError) as error:
        print(f"failed: {error}", file=sys.stderr)
        return 1

    print(f"published {result.payload.name}: {result.payload.conclusion}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
