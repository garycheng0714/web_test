"""Export Phoenix annotations for one designer eval run to labels.jsonl.

HUMAN annotations are the ground truth; CODE annotations carry the deterministic checks.
Run from the repository root:

    PYTHONPATH=. uv run --group eval python .scratch/designer-evals/export_labels.py \
        --run register-login-20261029T070829Z
"""

import argparse
import json
import os
import sys
from pathlib import Path

from web_test.paths import REPO_ROOT

RUNS_DIR = REPO_ROOT / ".scratch" / "designer-evals" / "runs"


def _base_url() -> str:
    base = os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006")
    return base.removesuffix("/v1/traces")


def _latest_run() -> Path:
    runs = [path for path in RUNS_DIR.iterdir() if (path / "run.json").exists()]
    if not runs:
        raise FileNotFoundError(f"no run artifacts under {RUNS_DIR}")
    return max(runs, key=lambda path: path.stat().st_mtime)


def _label_rows(
    units: list[dict],
    annotations: list[dict],
    run: dict,
    *,
    annotator: str,
) -> list[dict]:
    by_span: dict[str, list[dict]] = {}
    for annotation in annotations:
        by_span.setdefault(annotation["span_id"], []).append(annotation)

    rows = []
    for unit in units:
        for annotation in by_span.get(unit["span_id"], []):
            kind = annotation["annotator_kind"]
            result = annotation.get("result") or {}
            rows.append(
                {
                    "run_id": run["run_id"],
                    "prd": run["prd"],
                    "target_kind": unit["kind"],
                    "target_id": unit["target_id"],
                    "span_id": unit["span_id"],
                    "annotation": annotation["name"],
                    "annotator_kind": kind,
                    "label": result.get("label"),
                    "score": result.get("score"),
                    "annotator": annotator if kind == "HUMAN" else "code",
                    "explanation": result.get("explanation"),
                    "identifier": annotation.get("identifier", ""),
                    "annotation_id": annotation.get("id"),
                    "source": annotation.get("source"),
                    "metadata": annotation.get("metadata", {}),
                }
            )
    return sorted(
        rows,
        key=lambda row: (
            row["target_kind"],
            row["target_id"],
            row["annotation"],
            row["annotator_kind"],
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phoenix annotations to labels.jsonl.")
    parser.add_argument("--run", help="run id under .scratch/designer-evals/runs/")
    parser.add_argument("--project", help="Phoenix project; defaults to run.json")
    parser.add_argument("--annotator", default="local", help="annotator name for HUMAN rows")
    args = parser.parse_args()

    try:
        run_dir = RUNS_DIR / args.run if args.run else _latest_run()
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        units = json.loads((run_dir / "units.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"failed to read run artifacts: {error}", file=sys.stderr)
        return 1

    from phoenix.client import Client

    project = args.project or run["project"]
    client = Client(base_url=_base_url())
    annotations = client.spans.get_span_annotations(
        span_ids=[unit["span_id"] for unit in units],
        project_identifier=project,
    )
    rows = _label_rows(units, annotations, run, annotator=args.annotator)
    path = run_dir / "labels.jsonl"
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    human = sum(row["annotator_kind"] == "HUMAN" for row in rows)
    code = sum(row["annotator_kind"] == "CODE" for row in rows)
    print(f"run: {run['run_id']}")
    print(f"project: {project}")
    print(f"labels: {len(rows)} ({human} HUMAN, {code} CODE)")
    print(f"annotator: {args.annotator}")
    print(f"output: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
