import xml.etree.ElementTree as ET
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from web_test.write_guard import is_generated_test_path

MESSAGE_LIMIT = 200


class TestStatus(StrEnum):
    __test__ = False

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class TestOutcome:
    __test__ = False

    nodeid: str
    file: str
    status: TestStatus
    message: str = ""


@dataclass(frozen=True)
class RunReport:
    generated: tuple[TestOutcome, ...]
    failing: tuple[TestOutcome, ...]
    junit_available: bool = True


def _status(testcase: ET.Element) -> TestStatus:
    if testcase.find("skipped") is not None:
        return TestStatus.SKIPPED
    if testcase.find("failure") is not None or testcase.find("error") is not None:
        return TestStatus.FAILED
    return TestStatus.PASSED


def _message(testcase: ET.Element) -> str:
    for tag in ("failure", "error"):
        node = testcase.find(tag)
        if node is None:
            continue
        message = node.get("message") or (node.text or "")
        return message.splitlines()[0][:MESSAGE_LIMIT] if message else ""
    return ""


def parse_junit(text: str) -> tuple[TestOutcome, ...]:
    """Read pytest's JUnit XML into test outcomes."""
    root = ET.fromstring(text)  # noqa: S314 - pytest's own JUnit output, not remote input
    outcomes = []
    for testcase in root.iter("testcase"):
        classname = testcase.get("classname", "")
        name = testcase.get("name", "")
        outcomes.append(
            TestOutcome(
                nodeid=f"{classname}::{name}" if classname else name,
                file=testcase.get("file", ""),
                status=_status(testcase),
                message=_message(testcase),
            )
        )
    return tuple(outcomes)


def read_junit(path: Path) -> tuple[TestOutcome, ...] | None:
    """Read the JUnit file; a missing or malformed file is unavailable, not fatal."""
    try:
        return parse_junit(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ET.ParseError):
        return None


def build_run_report(
    outcomes: tuple[TestOutcome, ...] | None,
    files: Sequence[str],
) -> RunReport:
    if outcomes is None:
        return RunReport(generated=(), failing=(), junit_available=False)
    generated_files = {path for path in files if is_generated_test_path(path)}
    generated = tuple(outcome for outcome in outcomes if outcome.file in generated_files)
    failing = tuple(
        outcome
        for outcome in outcomes
        if outcome.file not in generated_files and outcome.status is TestStatus.FAILED
    )
    return RunReport(generated=generated, failing=failing)


def _line(outcome: TestOutcome) -> str:
    line = f"- `{outcome.status.value.upper()}` {outcome.nodeid}"
    if outcome.message:
        line += f" — {outcome.message}"
    return line


def _section(title: str, outcomes: tuple[TestOutcome, ...]) -> list[str]:
    lines = [f"### {title}", ""]
    lines += [_line(outcome) for outcome in outcomes] if outcomes else ["None."]
    return lines


def render_run_report(report: RunReport) -> str:
    lines = ["## Run report", ""]
    if not report.junit_available:
        lines.append("JUnit XML was unavailable; per-test results could not be read.")
        return "\n".join(lines)
    lines += _section("Generated tests", report.generated)
    lines += ["", *_section("Failing existing tests", report.failing)]
    return "\n".join(lines)
