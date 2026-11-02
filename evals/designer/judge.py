"""Judge designer claims against the PRD and report TPR/TNR.

This runs one LLM judgement per labeled claim. It is report-only and does not gate anything.

    PYTHONPATH=. uv run --group eval python evals/designer/judge.py \
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
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--run-id", help="output directory name")
    return parser.parse_args(argv)


_ATTEMPTS = 3


async def run_all(
    agent: Agent[None, JudgeOutput],
    examples: Sequence[JudgeExample],
    *,
    model_name: str,
    concurrency: int,
) -> list[JudgeRecord]:
    semaphore = asyncio.Semaphore(concurrency)

    async def one(example: JudgeExample) -> JudgeRecord:
        async with semaphore:
            last_error: Exception | None = None
            for attempt in range(_ATTEMPTS):
                try:
                    return await run_one(agent, example, model_name=model_name)
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
    examples = load_examples(data_dir)
    if args.source_run:
        examples = [example for example in examples if example.data.source_run == args.source_run]
    if args.limit is not None:
        examples = examples[: args.limit]
    if not examples:
        print(f"no labeled claims under {data_dir}", file=sys.stderr)
        return 1

    model_name = os.environ.get("WEB_TEST_JUDGE_MODEL") or DEFAULT_JUDGE_MODEL
    agent = Agent(resolve_judge_model(), output_type=JudgeOutput, instructions=SYSTEM_PROMPT)
    print(f"judging {len(examples)} claims with {model_name}...", file=sys.stderr)
    records = run_sync(
        run_all(agent, examples, model_name=model_name, concurrency=args.concurrency)
    )

    run_id = args.run_id or f"{args.dataset}-{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    run_dir = OUT_DIR / run_id
    write_records(run_dir / "judgements.jsonl", records)
    metrics = score(records)
    report = render_report(metrics)
    (run_dir / "report.md").write_text(report, encoding="utf-8")

    print(f"claims: {metrics.total}")
    print(f"verdicts: {metrics.passed} pass, {metrics.failed} fail")
    print(f"TPR: {metrics.tpr:.2f} CI [{metrics.tpr_ci[0]:.2f}, {metrics.tpr_ci[1]:.2f}]")
    print(f"TNR: {metrics.tnr:.2f} CI [{metrics.tnr_ci[0]:.2f}, {metrics.tnr_ci[1]:.2f}]")
    print(f"disagreements: {len(metrics.disagreements)}")
    print(f"artifacts: {run_dir.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
