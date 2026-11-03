"""Report coverage and code checks for one designer eval run.

Run from the repository root after export_labels.py:

    PYTHONPATH=. uv run --group eval python evals/designer/report.py \
        --run register-login-20261029T070829Z
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from evals.designer.designer_eval.metrics import wilson_interval
from evals.designer.designer_eval.units import RunFindings, UnitKind, case_id, duplicate_groups
from web_test.paths import REPO_ROOT
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.structure import structure_checks
from web_test.planning.review.verification import VerificationStatus
from web_test.planning.schema import DesignOutput

RUNS_DIR = REPO_ROOT / "evals" / "designer" / "runs"


def _claims(units: list[dict]) -> list[dict]:
    return [unit for unit in units if unit["kind"] == UnitKind.CLAIM]


def _latest_run() -> Path:
    runs = [path for path in RUNS_DIR.iterdir() if (path / "run.json").exists()]
    if not runs:
        raise FileNotFoundError(f"no run artifacts under {RUNS_DIR}")
    return max(runs, key=lambda path: path.stat().st_mtime)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_labels(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def requirement_rows(units: list[dict], labels: list[dict]) -> list[dict]:
    requirements: dict[str, dict] = {}
    for unit in units:
        if unit["kind"] != UnitKind.REQUIREMENT:
            continue
        attributes = unit["attributes"]
        requirement_id = attributes["requirement.id"]
        requirements[requirement_id] = {
            "requirement_id": requirement_id,
            "claim_ids": [],
            "case_ids": [],
            "missing": attributes.get("requirement.missing") == "true",
        }

    for unit in _claims(units):
        attributes = unit["attributes"]
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
        row["missing"] = False

    claim_labels: dict[str, list[dict]] = {}
    for label in labels:
        if label["annotator_kind"] == "HUMAN" and label["annotation"] == "claim_alignment":
            claim_labels.setdefault(label["target_id"], []).append(label)

    rows = []
    for requirement_id in sorted(requirements):
        item = requirements[requirement_id]
        relevant = [
            label for claim_id in item["claim_ids"] for label in claim_labels.get(claim_id, [])
        ]
        if item["missing"] or not item["claim_ids"]:
            status = "missing"
        elif not relevant:
            status = "unlabeled"
        elif any(label.get("label") == "pass" for label in relevant):
            status = "covered"
        else:
            status = "not_clean"
        rows.append(
            {
                **item,
                "status": status,
                "labels": relevant,
                "pass_count": sum(label.get("label") == "pass" for label in relevant),
                "tested": bool(item["claim_ids"]) and not item["missing"],
            }
        )
    return rows


def _human_fields(labels: list[dict]) -> dict[str, dict[str, dict]]:
    fields: dict[str, dict[str, dict]] = {}
    for label in labels:
        if label["annotator_kind"] != "HUMAN":
            continue
        fields.setdefault(label["target_id"], {})[label["annotation"]] = label
    return fields


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip() or "-"


def _empty_cases(design: dict) -> list[str]:
    validated = DesignOutput.model_validate(design)
    return [
        case_id(index, case.test_type)
        for index, case in enumerate(validated.cases, start=1)
        if not case.requirement_ids
    ]


def _prd_path(run: dict) -> Path | None:
    recorded = run.get("prd_path")
    if recorded:
        candidate = (REPO_ROOT / recorded).resolve()
        if candidate.exists():
            return candidate
    candidate = REPO_ROOT / "prd" / run["prd"]
    return candidate if candidate.exists() else None


def structure_failures(run_dir: Path, run: dict) -> tuple[list[str] | None, str]:
    text_path = run_dir / "test-case.md"
    prd_path = _prd_path(run)
    if not text_path.exists():
        return None, "test-case.md is missing"
    if prd_path is None:
        return None, f"PRD {run['prd']} not found"
    text = text_path.read_text(encoding="utf-8")
    try:
        subject = parse_test_case(text, prd_path.read_text(encoding="utf-8"))
        outcomes = structure_checks(subject, text)
    except ValueError as error:
        return [f"test-case.md: {error}"], ""
    return [
        f"{outcome.check_id}: {outcome.detail or outcome.label}"
        for outcome in outcomes
        if outcome.status is VerificationStatus.FAIL
    ], ""


def _duplicate_cases(design: dict) -> list[str]:
    groups = duplicate_groups(DesignOutput.model_validate(design))
    return sorted({cid for ids in groups.values() for cid in ids})


def _header_lines(run: dict, *, total: int, claim_count: int, human_labels: int) -> list[str]:
    return [
        f"# Designer eval report: {run['run_id']}",
        "",
        f"- PRD: `{run['prd']}`",
        f"- Model: `{run['model']}`",
        f"- Requirements: {total}",
        f"- Claims: {claim_count}",
        f"- HUMAN labels: {human_labels}",
    ]


def _coverage_lines(
    *,
    total: int,
    tested: int,
    clean: int,
    not_clean: list[dict],
    missing: list[dict],
    unlabeled: list[dict],
    low: float,
    high: float,
) -> list[str]:
    return [
        "",
        "## Coverage",
        "",
        f"- Tested: {tested} / {total} (has at least one claim)" if total else "- Tested: 0 / 0",
        f"- Clean: {clean} / {total} ({clean / total:.0%})" if total else "- Clean: 0 / 0",
        f"- Wilson 95% CI (clean): [{low:.2f}, {high:.2f}]" if total else "- Wilson 95% CI: n/a",
        f"- Not clean: {len(not_clean)}",
        f"- Missing: {len(missing)}",
        f"- Unlabeled: {len(unlabeled)}",
    ]


def _requirement_lines(rows: list[dict]) -> list[str]:
    lines = [
        "",
        "## Requirements",
        "",
        "| Requirement | Cases | Human labels | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        labels_text = (
            ", ".join(f"{label.get('label')}({label.get('annotator')})" for label in row["labels"])
            or "-"
        )
        lines.append(
            f"| {row['requirement_id']} | {', '.join(row['case_ids']) or '-'} | "
            f"{labels_text} | `{row['status']}` |"
        )
    return lines


def _failure_mode_lines(
    *, mode_counts: dict[str, int], fail_count: int, human_labels: int
) -> list[str]:
    lines = ["", "## Failure modes", ""]
    if not human_labels:
        return [*lines, "No HUMAN claim labels."]
    lines += ["| Failure mode | Claims |", "| --- | --- |"]
    for mode, count in sorted(mode_counts.items()):
        lines.append(f"| {mode} | {count} |")
    lines.append(f"| fail (total) | {fail_count} |")
    lines.append("")
    lines.append(f"Denominator: {human_labels} labeled claims.")
    return lines


def _claim_lines(units: list[dict], human_fields: dict[str, dict[str, dict]]) -> list[str]:
    lines = [
        "",
        "## Claims",
        "",
        "| Claim | Alignment | Failure mode | Reason |",
        "| --- | --- | --- | --- |",
    ]
    for unit in _claims(units):
        fields = human_fields.get(unit["target_id"], {})
        alignment = (fields.get("claim_alignment") or {}).get("label") or "-"
        mode = (fields.get("claim_failure_mode") or {}).get("label") or "-"
        reason = (fields.get("claim_reason") or {}).get("explanation") or "-"
        lines.append(f"| {unit['target_id']} | {alignment} | {mode} | {_cell(reason)} |")
    return lines


def _not_clean_lines(not_clean: list[dict]) -> list[str]:
    lines = ["", "## Requirements without a passing claim", ""]
    if not not_clean:
        return [*lines, "None."]
    for row in not_clean:
        labels_text = ", ".join(
            f"{label.get('target_id')}={label.get('label')}" for label in row["labels"]
        )
        lines.append(f"- {row['requirement_id']}: {labels_text}")
    return lines


def _code_check_lines(
    *,
    findings: RunFindings,
    empty_cases: list[str],
    duplicate_cases: list[str],
    structure_errors: list[str],
    structure_checked: bool,
    structure_note: str,
    missing: list[dict],
    unlabeled: list[dict],
) -> list[str]:
    lines = ["", "## Code checks", ""]
    non_requirement_count = sum(len(ids) for ids in findings.non_requirement_ids.values())
    lines.append(f"- Non-requirement IDs: {non_requirement_count}")
    for cid, ids in sorted(findings.non_requirement_ids.items()):
        lines.append(f"  - {cid}: {', '.join(ids)}")
    invalid_count = sum(len(ids) for ids in findings.invalid_requirement_ids.values())
    lines.append(f"- Invalid requirement IDs: {invalid_count}")
    for cid, ids in sorted(findings.invalid_requirement_ids.items()):
        lines.append(f"  - {cid}: {', '.join(ids)}")
    multi = findings.multi_requirement_cases
    lines.append(
        f"- Multi-requirement cases: {len(multi)}" + (f" ({', '.join(multi)})" if multi else "")
    )
    lines.append(
        f"- Empty requirement_ids: {len(empty_cases)}"
        + (f" ({', '.join(empty_cases)})" if empty_cases else "")
    )
    lines.append(
        f"- Duplicate cases: {len(duplicate_cases)}"
        + (f" ({', '.join(duplicate_cases)})" if duplicate_cases else "")
    )
    if structure_checked:
        lines.append(f"- Structure failures: {len(structure_errors)}")
    elif structure_note:
        lines.append(f"- Structure failures: not checked ({structure_note})")
    else:
        lines.append("- Structure failures: not checked")
    for error in structure_errors:
        lines.append(f"  - {error}")
    if missing:
        lines.append(
            f"- Missing requirements: {', '.join(row['requirement_id'] for row in missing)}"
        )
    if unlabeled:
        lines.append(
            "- Unlabeled requirements: " + ", ".join(row["requirement_id"] for row in unlabeled)
        )
    return lines


def _limits_lines() -> list[str]:
    return [
        "",
        "## Limits",
        "",
        "- Small PRD sample; the Wilson CI is wide.",
        (
            "- `Clean` requires at least one passing claim; a case with one extra assertion makes "
            "its requirement not clean even though it exercises the requirement. `Tested` counts "
            "requirements with at least one claim."
        ),
        (
            "- Coverage treats unlabeled claims as not clean; finish labeling before trusting the "
            "number."
        ),
        (
            "- A case claiming multiple requirements produces multiple claim labels and is flagged "
            "as a multi-requirement case."
        ),
    ]


def render_report(
    *,
    run: dict,
    units: list[dict],
    labels: list[dict],
    design: dict,
    structure_errors: list[str] | None = None,
    structure_note: str = "",
    findings: RunFindings | None = None,
) -> str:
    rows = requirement_rows(units, labels)
    total = len(rows)
    tested = sum(row["tested"] for row in rows)
    clean = sum(row["status"] == "covered" for row in rows)
    not_clean = [row for row in rows if row["status"] == "not_clean"]
    missing = [row for row in rows if row["status"] == "missing"]
    unlabeled = [row for row in rows if row["status"] == "unlabeled"]
    low, high = wilson_interval(clean, total)
    human_fields = _human_fields(labels)
    aligned = {
        target: fields["claim_alignment"]
        for target, fields in human_fields.items()
        if "claim_alignment" in fields
    }
    human_labels = len(aligned)
    mode_counts: dict[str, int] = {}
    for target, label in aligned.items():
        mode = (human_fields[target].get("claim_failure_mode") or {}).get("label")
        if label.get("label") == "fail" and mode:
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
    fail_count = sum(label.get("label") == "fail" for label in aligned.values())
    findings = findings or RunFindings()

    lines = _header_lines(
        run, total=total, claim_count=len(_claims(units)), human_labels=human_labels
    )
    lines += _coverage_lines(
        total=total,
        tested=tested,
        clean=clean,
        not_clean=not_clean,
        missing=missing,
        unlabeled=unlabeled,
        low=low,
        high=high,
    )
    lines += _requirement_lines(rows)
    lines += _failure_mode_lines(
        mode_counts=mode_counts, fail_count=fail_count, human_labels=human_labels
    )
    lines += _claim_lines(units, human_fields)
    lines += _not_clean_lines(not_clean)
    lines += _code_check_lines(
        findings=findings,
        empty_cases=_empty_cases(design),
        duplicate_cases=_duplicate_cases(design),
        structure_errors=structure_errors or [],
        structure_checked=structure_errors is not None,
        structure_note=structure_note,
        missing=missing,
        unlabeled=unlabeled,
    )
    lines += _limits_lines()
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Report designer eval coverage.")
    parser.add_argument("--run", help="run id under .scratch/designer-evals/runs/")
    parser.add_argument("--run-dir", help="explicit run directory")
    args = parser.parse_args()

    try:
        if args.run_dir:
            run_dir = Path(args.run_dir)
        elif args.run:
            run_dir = RUNS_DIR / args.run
        else:
            run_dir = _latest_run()
        run = _load_json(run_dir / "run.json")
        units = _load_json(run_dir / "units.json")
        design = _load_json(run_dir / "design.json")
        labels = _load_labels(run_dir / "labels.jsonl")
    except (OSError, ValueError) as error:
        print(f"failed to read run artifacts: {error}", file=sys.stderr)
        return 1

    structure_errors, structure_note = structure_failures(run_dir, run)
    report = render_report(
        run=run,
        units=units,
        labels=labels,
        design=design,
        structure_errors=structure_errors,
        structure_note=structure_note,
        findings=RunFindings.model_validate(run),
    )
    path = run_dir / "report.md"
    path.write_text(report, encoding="utf-8")
    print(report)
    print(f"output: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
