"""Judge designer claims against the PRD and report TPR/TNR.

This runs one LLM judgement per labeled claim. It is report-only and does not gate anything.

    PYTHONPATH=. uv run --group eval python evals/designer/run_judge.py \
        --dataset automationexercise --limit 10
"""

import argparse
import asyncio
import os
import sys
from collections.abc import Sequence
from datetime import UTC, datetime

from pydantic_ai import Agent

from evals.designer.designer_eval.judge import (
    SYSTEM_PROMPT,
    JudgeExample,
    JudgeOutput,
    JudgeRecord,
    format_rate,
    group_by_source,
    load_examples,
    render_report,
    run_one,
    score,
    write_records,
)
from web_test._run import run_sync
from web_test.model import DEFAULT_JUDGE_MODEL, resolve_judge_model
from web_test.paths import REPO_ROOT

DATA_DIR = REPO_ROOT / "evals" / "designer" / "judge" / "data"
OUT_DIR = REPO_ROOT / "evals" / "designer" / "judge" / "runs"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Judge designer claims against the PRD.")
    parser.add_argument("--dataset", default="automationexercise")
    parser.add_argument("--limit", type=int, help="judge only the first N claims")
    parser.add_argument("--source-run", help="judge only claims from one source run")
    parser.add_argument(
        "--include-multi-fr",
        action="store_true",
        help="also judge legacy multi-requirement cases (historical analysis only)",
    )
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument(
        "--claim-id",
        action="append",
        help="judge only these claim ids (repeatable); needed for stability experiments",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="override the model temperature (default: leave it to the provider)",
    )
    parser.add_argument("--run-id", help="output directory name")
    return parser.parse_args(argv)


_ATTEMPTS = 3


async def run_all(
    agent: Agent[None, JudgeOutput],
    examples: Sequence[JudgeExample],
    *,
    model_name: str,
    concurrency: int,
    temperature: float | None = None,
) -> list[JudgeRecord]:
    semaphore = asyncio.Semaphore(concurrency)

    async def one(example: JudgeExample) -> JudgeRecord:
        async with semaphore:
            last_error: Exception | None = None
            for attempt in range(_ATTEMPTS):
                try:
                    return await run_one(
                        agent, example, model_name=model_name, temperature=temperature
                    )
                except Exception as error:
                    last_error = error
                    if attempt < _ATTEMPTS - 1:
                        await asyncio.sleep(2**attempt)
            if last_error is not None:
                raise last_error
            raise RuntimeError("judge retry loop finished without a result")

    return list(await asyncio.gather(*(one(example) for example in examples)))


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    data_dir = DATA_DIR / args.dataset
    examples = load_examples(data_dir, single_fr_only=not args.include_multi_fr)
    if args.source_run:
        examples = [example for example in examples if example.data.source_run == args.source_run]
    if args.claim_id:
        wanted = set(args.claim_id)
        examples = [example for example in examples if example.data.claim_id in wanted]
        missing = wanted - {example.data.claim_id for example in examples}
        if missing:
            print(f"unknown claim ids: {sorted(missing)}", file=sys.stderr)
            return 1
    if args.limit is not None:
        examples = examples[: args.limit]
    if not examples:
        print(f"no labeled claims under {data_dir}", file=sys.stderr)
        return 1

    model_name = os.environ.get("WEB_TEST_JUDGE_MODEL") or DEFAULT_JUDGE_MODEL
    agent = Agent(resolve_judge_model(), output_type=JudgeOutput, instructions=SYSTEM_PROMPT)
    print(
        f"judging {len(examples)} claims with {model_name}"
        + (f" at temperature {args.temperature}" if args.temperature is not None else ""),
        file=sys.stderr,
    )
    records = run_sync(
        run_all(
            agent,
            examples,
            model_name=model_name,
            concurrency=args.concurrency,
            temperature=args.temperature,
        )
    )

    run_id = args.run_id or f"{args.dataset}-{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    run_dir = OUT_DIR / run_id
    write_records(run_dir / "judgements.jsonl", records)
    metrics = score(records)
    report = render_report(metrics, group_by_source(records))
    (run_dir / "report.md").write_text(report, encoding="utf-8")

    print(f"claims: {metrics.total}")
    print(f"human labels: {metrics.human_fail} fail, {metrics.human_pass} pass")
    print(f"judge verdicts: {metrics.judged_fail} fail, {metrics.judged_pass} pass")
    print(f"fail recall: {format_rate(metrics.fail_recall, metrics.fail_recall_ci)}")
    print(f"pass specificity: {format_rate(metrics.pass_specificity, metrics.pass_specificity_ci)}")
    print(f"disagreements: {len(metrics.disagreements)}")
    print(f"artifacts: {run_dir.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
