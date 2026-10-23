import argparse
import os
import sys
from pathlib import Path

from web_test.planning.verify.cache import VerdictCache
from web_test.planning.verify.input import Approval, PreparedVerification
from web_test.planning.verify.prepare import prepare
from web_test.planning.verify.run import run
from web_test.publishing.github import GitHubAdapter


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


def _approval(args: argparse.Namespace) -> Approval | None:
    values = (args.approval_state, args.approval_reason, args.approval_head_sha)
    if all(value is None for value in values):
        return None
    if any(value is None for value in values):
        raise ValueError("approval flags must be provided together")
    return Approval(
        state=args.approval_state,
        reason=args.approval_reason,
        head_sha=args.approval_head_sha,
    )


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
    run_parser.add_argument("--approval-state")
    run_parser.add_argument("--approval-reason")
    run_parser.add_argument("--approval-head-sha")
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
        approval = _approval(args)
        result = run(
            prepared_verification,
            head_sha=args.head_sha,
            name=args.check_name,
            publish=GitHubAdapter.from_env().publish_check,
            cache=cache,
            approval=approval,
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
