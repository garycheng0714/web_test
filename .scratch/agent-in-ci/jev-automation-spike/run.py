import argparse
import asyncio
import importlib
import json
from pathlib import Path

from typesafe_sdk import AsyncTypeSafeClient, NoulAnswer

MODEL = "jev-1.13.0"
RUNS = 3
ROOT = Path(__file__).resolve().parent

VARIANTS = ("good", "skip", "substitute", "wrong_expected")
INTENDED = {
    "skip": "expected_results_asserted",
    "substitute": "steps_in_order",
    "wrong_expected": "expected_results_asserted",
}


def _support() -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "support").rglob("*.py"))
    }


def _answers(response: object) -> dict[str, float | None]:
    answers = getattr(response, "answers")
    return {
        name: answer.noul if isinstance(answer, NoulAnswer) else None
        for name, answer in answers.items()
    }


def _records_pass(
    records: list[dict[str, object]], questions: dict[str, object]
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    good = [record for record in records if record["variant"] == "good"]
    for question in questions:
        values = [record["answers"].get(question) for record in good]  # type: ignore[union-attr]
        if sum(1 for value in values if value is not None and value >= 0.8) < 2:
            reasons.append(f"good: {question} did not reach 0.8 in 2/3 runs")

    for variant, question in INTENDED.items():
        runs = [record for record in records if record["variant"] == variant]
        values = [record["answers"].get(question) for record in runs]  # type: ignore[union-attr]
        if any(value is None for value in values):
            reasons.append(f"{variant}: {question} returned no answer")
        elif sum(1 for value in values if value < 0.5) < 2:
            reasons.append(f"{variant}: {question} did not fall below 0.5 in 2/3 runs")

    return not reasons, reasons


def _print_table(
    records: list[dict[str, object]], questions: dict[str, object]
) -> None:
    print(f"\nmodel: {MODEL}, runs per variant: {RUNS}")
    print(f"{'variant':16} {'question':28} {'run1':>6} {'run2':>6} {'run3':>6}")
    for variant in VARIANTS:
        runs = [record for record in records if record["variant"] == variant]
        for question in questions:
            values = [record["answers"].get(question) for record in runs]  # type: ignore[union-attr]
            cells = " ".join(f"{value:6.3f}" if value is not None else "  none" for value in values)
            print(f"{variant:16} {question:28} {cells}")


async def main(questions_name: str, output: str) -> int:
    questions = importlib.import_module(questions_name).QUESTIONS
    case = (ROOT / "case.md").read_text(encoding="utf-8")
    support = _support()
    records: list[dict[str, object]] = []

    async with AsyncTypeSafeClient() as client:
        for variant in VARIANTS:
            subject = {
                "case": case,
                "test": (ROOT / "variants" / f"{variant}.py").read_text(encoding="utf-8"),
                "support": support,
            }
            for run in range(1, RUNS + 1):
                response = await client.system_one(subject, questions, model=MODEL)
                record = {
                    "variant": variant,
                    "run": run,
                    "model": response.model,
                    "answers": _answers(response),
                    "usage": json.loads(response.usage.model_dump_json()),
                }
                records.append(record)
                print(f"{variant} run {run}: {record['answers']}", flush=True)

    (ROOT / output).write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    _print_table(records, questions)
    passed, reasons = _records_pass(records, questions)
    print("\nkill criteria:", "PASS" if passed else "FAIL")
    for reason in reasons:
        print(f"- {reason}")
    return 0 if passed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", default="questions", help="module name in this directory")
    parser.add_argument("--output", default="raw.json", help="output JSON file")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.questions, args.output)))
