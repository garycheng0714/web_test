import ast
import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath

from web_test.write_guard import is_generated_test_path

_CASE_HEADING = re.compile(r"(?m)^## Case (\d+):")
_PAGE_OBJECT_PACKAGES = {"pages", "components"}
_DIRECT_PAGE_METHODS = frozenset(
    {
        "goto",
        "locator",
        "get_by_role",
        "get_by_text",
        "get_by_label",
        "get_by_placeholder",
        "get_by_alt_text",
        "get_by_title",
        "get_by_test_id",
        "query_selector",
        "query_selector_all",
        "frame_locator",
    }
)


class QualityRule(StrEnum):
    CASE_MARKER = "case_marker"
    CASE_COVERAGE = "case_coverage"
    ASSERTION = "assertion"
    PAGE_OBJECT = "page_object"
    TESTS_LOCATION = "tests_location"
    PAGE_OBJECT_IMPORT = "page_object_import"
    SYNTAX = "syntax"


@dataclass(frozen=True)
class QualityFinding:
    """One deterministic reason the generated tests cannot be published."""

    rule: QualityRule
    detail: str


def _case_numbers(text: str) -> set[int]:
    return {int(match.group(1)) for match in _CASE_HEADING.finditer(text)}


def _source_path(relative: str, workspace: Path) -> Path | None:
    candidate = PurePosixPath(relative)
    if (
        candidate.is_absolute()         # 拒絕絕對路徑（如 /etc/passwd）
        or not candidate.parts          # 空路徑（""）
        or ".." in candidate.parts      # 拒絕目錄穿越（../）
        or candidate.suffix != ".py"    # 只收 Python 檔
    ):
        return None
    path = workspace / Path(*candidate.parts)
    try:
        resolved = path.resolve()
    except OSError:
        return None
    if not resolved.is_relative_to(workspace.resolve()) or not resolved.is_file():
        return None
    return path


def _test_functions(tree: ast.Module) -> list[ast.FunctionDef]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]


def _markers(function: ast.FunctionDef) -> list[tuple[str, int]]:
    markers: list[tuple[str, int]] = []
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        if not isinstance(decorator.func, ast.Attribute) or decorator.func.attr != "case":
            continue
        owner = decorator.func.value
        if not (isinstance(owner, ast.Attribute) and owner.attr == "mark"):
            continue
        if len(decorator.args) < 2:
            continue
        first, second = decorator.args[0], decorator.args[1]
        if not (isinstance(first, ast.Constant) and isinstance(second, ast.Constant)):
            continue
        file_id, number = first.value, second.value
        if (
            isinstance(file_id, str)
            and isinstance(number, int)
            and not isinstance(number, bool)
        ):
            markers.append((file_id, number))
    return markers


def _is_page(node: ast.expr) -> bool:
    if isinstance(node, ast.Name):
        return node.id == "page"
    return isinstance(node, ast.Attribute) and node.attr == "page"


def _direct_page_calls(function: ast.FunctionDef) -> list[str]:
    calls = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr in _DIRECT_PAGE_METHODS and _is_page(node.func.value):
            calls.append(node.func.attr)
    return calls


def _asserts(function: ast.FunctionDef) -> bool:
    for node in ast.walk(function):
        if isinstance(node, ast.Assert):
            return True
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "expect":
                return True
    return False


def _imports_page_objects(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            package = (node.module or "").split(".")[0]
            if package in _PAGE_OBJECT_PACKAGES:
                return True
        elif isinstance(node, ast.Import):
            if any(
                alias.name.split(".")[0] in _PAGE_OBJECT_PACKAGES for alias in node.names
            ):
                return True
    return False


def _where(relative: str, function: ast.FunctionDef) -> str:
    return f"{relative}:{function.lineno} ({function.name})"


def quality_findings(
    case_id: str,
    case_text: str,
    files: Sequence[str],
    workspace: Path,
) -> tuple[QualityFinding, ...]:
    """Check the generated tests against the case file and the page-object rules."""
    cases = _case_numbers(case_text)
    covered: set[int] = set()
    findings: list[QualityFinding] = []

    for relative in sorted(dict.fromkeys(files)):
        path = _source_path(relative, workspace)
        if path is None:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except SyntaxError as error:
            findings.append(
                QualityFinding(
                    QualityRule.SYNTAX,
                    f"{relative}: cannot parse ({error.msg})",
                )
            )
            continue
        except OSError:
            continue

        tests = _test_functions(tree)
        if not tests:
            continue

        if not is_generated_test_path(relative):
            findings.append(
                QualityFinding(
                    QualityRule.TESTS_LOCATION,
                    f"{relative}: generated tests must live under tests/",
                )
            )
        if not _imports_page_objects(tree):
            findings.append(
                QualityFinding(
                    QualityRule.PAGE_OBJECT_IMPORT,
                    f"{relative}: imports neither pages nor components",
                )
            )

        for function in tests:
            where = _where(relative, function)
            markers = _markers(function)
            if not markers:
                findings.append(
                    QualityFinding(
                        QualityRule.CASE_MARKER,
                        f"{where}: no @pytest.mark.case marker",
                    )
                )
            for file_id, number in markers:
                if file_id != case_id:
                    findings.append(
                        QualityFinding(
                            QualityRule.CASE_MARKER,
                            f"{where}: marker id {file_id!r} does not match {case_id!r}",
                        )
                    )
                elif number not in cases:
                    findings.append(
                        QualityFinding(
                            QualityRule.CASE_MARKER,
                            f"{where}: marker for case {number} does not exist",
                        )
                    )
                else:
                    covered.add(number)

            if not _asserts(function):
                findings.append(
                    QualityFinding(
                        QualityRule.ASSERTION,
                        f"{where}: has no assert or expect(...)",
                    )
                )
            for method in _direct_page_calls(function):
                findings.append(
                    QualityFinding(
                        QualityRule.PAGE_OBJECT,
                        f"{where}: calls page.{method}; use a page object",
                    )
                )

    for number in sorted(cases - covered):
        findings.append(
            QualityFinding(
                QualityRule.CASE_COVERAGE,
                f"case {number}: no test carries "
                f"@pytest.mark.case({case_id!r}, {number})",
            )
        )
    return tuple(findings)
