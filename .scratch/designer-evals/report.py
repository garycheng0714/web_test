"""Report coverage and code checks for one designer eval run.

Run from the repository root after export_labels.py:

    PYTHONPATH=. uv run --group eval python .scratch/designer-evals/report.py \
        --run register-login-20261029T070829Z
"""

import argparse
import json
import math
import sys
from pathlib import Path

from web_test.paths import REPO_ROOT
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.structure import structure_checks
from web_test.planning.review.verification import VerificationStatus

RUNS_DIR = REPO_ROOT / ".scratch" / "designer-evals" / "runs"


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    half = (
        z
        * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))
        / denominator
    )
    return (max(0.0, centre - half), min(1.0, centre + half))


def _latest_run() -> Path:
    runs = [path for path in RUNS_DIR.iterdir() if (path / "run.json").exists()]
    if not runs:
        raise FileNotFoundError(f"no run artifacts under {RUNS_DIR}")
    return max(runs, key=lambda path: path.stat().st_mtime)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_labels(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def requirement_rows(units: list[dict], labels: list[dict]) -> list[dict]:
    requirements: dict[str, dict] = {}
    invented: list[str] = []
    for unit in units:
        attributes = unit["attributes"]
        if unit["kind"] == "claim":
            if attributes.get("claim.requirement_exists") != "true":
                invented.append(unit["target_id"])
                continue
            requirement_id = attributes["requirement.id"]
            row = requirements.setdefault(
                requirement_id,
                {
                    "requirement_id": requirement_id,
                    "claim_ids": [],
                    "case_ids": [],
                    "missing": False,
                },
            )
            row["claim_ids"].append(unit["target_id"])
            row["case_ids"].append(attributes["claim.case_id"])
        elif unit["kind"] == "requirement" and attributes.get("requirement.missing") == "true":
            requirement_id = attributes["requirement.id"]
            requirements.setdefault(
                requirement_id,
                {
                    "requirement_id": requirement_id,
                    "claim_ids": [],
                    "case_ids": [],
                    "missing": True,
                },
            )

    claim_labels: dict[str, list[dict]] = {}
    for label in labels:
        if label["annotator_kind"] == "HUMAN" and label["annotation"] == "claim_alignment":
            claim_labels.setdefault(label["target_id"], []).append(label)

    rows = []
    for requirement_id in sorted(requirements):
        item = requirements[requirement_id]
        relevant = [
            label
            for claim_id in item["claim_ids"]
            for label in claim_labels.get(claim_id, [])
        ]
        if item["missing"]:
            status = "missing"
        elif not relevant:
            status = "unlabeled"
        elif any(label.get("label") == "pass" for label in relevant):
            status = "covered"
        else:
            status = "not_covered"
        rows.append(
            {
                **item,
                "status": status,
                "labels": relevant,
                "pass_count": sum(label.get("label") == "pass" for label in relevant),
            }
        )
    return rows, invented


def _empty_cases(design: dict) -> list[str]:
    return [
        f"case-{index}"
        for index, case in enumerate(design.get("cases", []), start=1)
        if not case.get("requirement_ids")
    ]


def structure_failures(run_dir: Path, prd_name: str) -> list[str]:
    text_path = run_dir / "test-case.md"
    prd_path = REPO_ROOT / "prd" / prd_name
    if not text_path.exists() or not prd_path.exists():
        return []
    text = text_path.read_text(encoding="utf-8")
    try:
        subject = parse_test_case(text, prd_path.read_text(encoding="utf-8"))
        outcomes = structure_checks(subject, text)
    except ValueError as error:
        return [f"test-case.md: {error}"]
    return [
        f"{outcome.check_id}: {outcome.detail or outcome.label}"
        for outcome in outcomes
        if outcome.status is VerificationStatus.FAIL
    ]


def _duplicate_cases(labels: list[dict]) -> list[str]:
    duplicates = set()
    for label in labels:
        if (
            label["annotator_kind"] == "CODE"
            and label["annotation"] == "case_duplicate"
            and label["label"] == "duplicate"
        ):
            case_id = label.get("metadata", {}).get("case_id")
            if case_id:
                duplicates.add(case_id)
    return sorted(duplicates)


def render_report(
    *,
    run: dict,
    units: list[dict],
    labels: list[dict],
    design: dict,
    structure_errors: list[str] | None = None,
) -> str:
    rows, invented = requirement_rows(units, labels)
    total = len(rows)
    covered = sum(row["status"] == "covered" for row in rows)
    not_covered = [row for row in rows if row["status"] == "not_covered"]
    missing = [row for row in rows if row["status"] == "missing"]
    unlabeled = [row for row in rows if row["status"] == "unlabeled"]
    low, high = wilson_interval(covered, total)
    human_labels = sum(label["annotator_kind"] == "HUMAN" for label in labels)
    claim_count = sum(unit["kind"] == "claim" for unit in units)
    empty_cases = _empty_cases(design)
    duplicate_cases = _duplicate_cases(labels)
    structure_errors = structure_errors or []

    lines = [
        f"# Designer eval report: {run['run_id']}",
        "",
        f"- PRD: `{run['prd']}`",
        f"- Model: `{run['model']}`",
        f"- Requirements: {total}",
        f"- Claims: {claim_count}",
        f"- HUMAN labels: {human_labels}",
        "",
        "## Coverage",
        "",
        f"- Covered: {covered} / {total} ({covered / total:.0%})" if total else "- Covered: 0 / 0",
        f"- Wilson 95% CI: [{low:.2f}, {high:.2f}]" if total else "- Wilson 95% CI: n/a",
        f"- Not covered: {len(not_covered)}",
        f"- Missing: {len(missing)}",
        f"- Unlabeled: {len(unlabeled)}",
        "",
        "## Requirements",
        "",
        "| Requirement | Cases | Human labels | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        labels_text = ", ".join(
            f"{label.get('label')}({label.get('annotator')})" for label in row["labels"]
        ) or "-"
        lines.append(
            f"| {row['requirement_id']} | {', '.join(row['case_ids']) or '-'} | "
            f"{labels_text} | `{row['status']}` |"
        )

    lines += ["", "## False tags", ""]
    if not_covered:
        for row in not_covered:
            labels_text = ", ".join(
                f"{label.get('target_id')}={label.get('label')}"
                for label in row["labels"]
            )
            lines.append(f"- {row['requirement_id']}: {labels_text}")
    else:
        lines.append("None.")

    lines += ["", "## Code checks", ""]
    lines.append(f"- Invented IDs: {len(invented)}" + (f" ({', '.join(invented)})" if invented else ""))
    lines.append(f"- Empty requirement_ids: {len(empty_cases)}" + (f" ({', '.join(empty_cases)})" if empty_cases else ""))
    lines.append(
        f"- Duplicate cases: {len(duplicate_cases)}"
        + (f" ({', '.join(duplicate_cases)})" if duplicate_cases else "")
    )
    lines.append(f"- Structure failures: {len(structure_errors)}")
    for error in structure_errors:
        lines.append(f"  - {error}")
    if missing:
        lines.append(f"- Missing requirements: {', '.join(row['requirement_id'] for row in missing)}")
    if unlabeled:
        lines.append(
            "- Unlabeled requirements: "
            + ", ".join(row["requirement_id"] for row in unlabeled)
        )

    lines += [
        "",
        "## Limits",
        "",
        "- Small PRD sample; the Wilson CI is wide.",
        "- Coverage treats unlabeled requirements as not covered; finish labeling before trusting the number.",
        "- A case claiming multiple requirements produces multiple claim labels.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Report designer eval coverage.")
    parser.add_argument("--run", help="run id under .scratch/designer-evals/runs/")
    args = parser.parse_args()

    try:
        run_dir = RUNS_DIR / args.run if args.run else _latest_run()
        run = _load_json(run_dir / "run.json")
        units = _load_json(run_dir / "units.json")
        design = _load_json(run_dir / "design.json")
        labels = _load_labels(run_dir / "labels.jsonl")
    except (OSError, ValueError) as error:
        print(f"failed to read run artifacts: {error}", file=sys.stderr)
        return 1

    report = render_report(
        run=run,
        units=units,
        labels=labels,
        design=design,
        structure_errors=structure_failures(run_dir, run["prd"]),
    )
    path = run_dir / "report.md"
    path.write_text(report, encoding="utf-8")
    print(report)
    print(f"output: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
