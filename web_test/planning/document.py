from pathlib import Path

from web_test.paths import TEST_CASES_PATH
from web_test.planning.schema import Case, QaReport

DRAFT = "draft"
APPROVED = "approved"

COLUMNS = (
    "Test Case ID",
    "Requirement IDs",
    "Module / Feature",
    "Test Scenario",
    "Preconditions",
    "Test Steps",
    "Test Data",
    "Expected Result",
    "Priority",
    "Severity",
    "Test Type",
    "Status",
    "Notes",
)


class ApprovedDocumentError(Exception):
    pass


def _cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "; ".join(str(item) for item in value)
    return str(value)


def _escape(value: object) -> str:
    return _cell(value).replace("|", "\\|").replace("\n", " ")


def _front_matter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def is_approved(path: str | Path) -> bool:
    return _front_matter(Path(path).read_text(encoding="utf-8")).get("approval") == APPROVED


def _section(title: str, items: list[str]) -> list[str]:
    lines = [f"## {title}", ""]
    lines += [f"- {item}" for item in items] if items else ["None identified"]
    lines.append("")
    return lines


def _row(case: Case) -> str:
    values = (
        case.test_case_id,
        case.requirement_ids,
        case.module_feature,
        case.test_scenario,
        case.preconditions,
        case.test_steps,
        case.test_data,
        case.expected_result,
        case.priority,
        case.severity,
        case.test_type,
        case.status,
        case.notes,
    )
    return "| " + " | ".join(_escape(value) for value in values) + " |"


def _table(cases: list[Case]) -> str:
    header = "| " + " | ".join(COLUMNS) + " |"
    separator = "| " + " | ".join("---" for _ in COLUMNS) + " |"
    rows = [_row(case) for case in cases]
    return "\n".join([header, separator, *rows])


def render(report: QaReport) -> str:
    parts = ["---", f"approval: {DRAFT}", "---", ""]
    parts += _section("Requirement Summary", report.requirement_summary)
    parts += _section("Coverage Areas", report.coverage_areas)
    parts += _section("Assumptions", report.assumptions)
    parts += _section("Clarifications Needed", report.clarifications_needed)
    parts += ["## Test Cases", "", _table(report.test_cases), ""]
    parts += _section("Missing/Unclear Requirements", report.missing_unclear_requirements)
    parts += _section("Suggested Improvements", report.suggested_improvements)
    return "\n".join(parts).rstrip() + "\n"


def write_report(
    report: QaReport, path: str | Path = TEST_CASES_PATH, *, force: bool = False
) -> None:
    target = Path(path)
    if target.exists() and is_approved(target) and not force:
        raise ApprovedDocumentError(
            f"{target} is approved; refusing to overwrite (pass force=True)."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(report), encoding="utf-8")
