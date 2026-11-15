"""Build a judge dataset from one designer run's units and exported Phoenix labels.

`export_labels.py` writes the annotations as a long-format `labels.jsonl`; the judge reads a
wide-format `claims.jsonl`. This joins the two by span id, so a claim that was never labeled stops
the build instead of becoming a row nobody checked.

Run from the repository root:

    PYTHONPATH=. uv run --group eval python evals/designer/build_claims.py \
        --run journey-v07-20261103 --out judge/data/automationexercise/claims.jsonl
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from evals.designer.designer_eval.artifacts import RunSummary, read_run, read_units
from evals.designer.designer_eval.dataset import LabeledClaim
from evals.designer.designer_eval.labels import AnnotationRow, human_fields, read_labels
from evals.designer.designer_eval.units import EvalUnit, UnitKind
from web_test.paths import REPO_ROOT

RUNS_DIR = REPO_ROOT / "evals" / "designer" / "runs"
NO_MODE = {None, "N/A"}


def _latest_run() -> Path:
    runs = [path for path in RUNS_DIR.iterdir() if (path / "labels.jsonl").is_file()]
    if not runs:
        raise FileNotFoundError(f"no exported run under {RUNS_DIR}")
    return max(runs, key=lambda path: path.stat().st_mtime)


def _field(
    fields: dict[str, AnnotationRow],
    name: str,
    field: Literal["label", "explanation"] = "label",
) -> str | None:
    row = fields.get(name)
    value = getattr(row, field) if row else None
    return value if isinstance(value, str) and value.strip() else None


def build_rows(
    units: Sequence[EvalUnit], labels: Sequence[AnnotationRow], run: RunSummary
) -> list[LabeledClaim]:
    """Join claim units with their human labels; refuse a claim that is not fully labeled."""
    by_span = human_fields(labels, by="span_id")
    rows: list[LabeledClaim] = []
    unlabeled: list[str] = []
    for unit in units:
        if unit.kind != UnitKind.CLAIM:
            continue
        fields = by_span.get(unit.span_id, {})
        alignment = _field(fields, "claim_alignment")
        if alignment is None:
            unlabeled.append(unit.target_id)
            continue
        if alignment not in ("pass", "fail"):
            raise ValueError(f"{unit.target_id} has an unknown claim_alignment {alignment!r}")
        human_label: Literal["pass", "fail"] = "pass" if alignment == "pass" else "fail"
        mode = _field(fields, "claim_failure_mode")
        if human_label == "pass":
            # Phoenix cannot clear a value, so a mode left on a passing claim means nothing.
            mode = None
        elif mode in NO_MODE:
            raise ValueError(f"{unit.target_id} failed without a failure mode")
        rows.append(
            LabeledClaim(
                source_run=run.run_id,
                claim_id=unit.target_id,
                requirement_id=unit.attributes["claim.requirement_id"],
                case_id=unit.attributes["claim.case_id"],
                case_markdown=unit.attributes["output.value"],
                human_label=human_label,
                human_mode=mode,
                human_reason=_field(fields, "claim_reason", "explanation"),
            )
        )
    if unlabeled:
        raise ValueError("claims without a claim_alignment: " + ", ".join(unlabeled))
    return sorted(rows, key=lambda row: row.claim_id)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a judge claims.jsonl from one run.")
    parser.add_argument("--run", help="run id under evals/designer/runs/ (default: latest)")
    parser.add_argument("--run-dir", help="explicit run directory")
    parser.add_argument("--out", help="output path (default: <run>/claims.jsonl)")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run_dir = (
            Path(args.run_dir)
            if args.run_dir
            else (RUNS_DIR / args.run if args.run else _latest_run())
        )
        run = read_run(run_dir)
        units = read_units(run_dir)
        labels = read_labels(run_dir / "labels.jsonl")
        rows = build_rows(units, labels, run)
    except (OSError, ValueError, KeyError) as error:
        print(f"failed: {error}", file=sys.stderr)
        return 1

    out = Path(args.out) if args.out else run_dir / "claims.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "".join(row.model_dump_json(exclude_none=False) + "\n" for row in rows), encoding="utf-8"
    )
    passed = sum(row.human_label == "pass" for row in rows)
    print(f"rows: {len(rows)} ({passed} pass, {len(rows) - passed} fail)")
    print(f"output: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
