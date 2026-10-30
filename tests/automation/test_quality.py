from pathlib import Path

import pytest

from web_test.automation.quality import QualityRule, quality_findings

CASE = """
## Case 1: Account / Register

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Open the page. | The page is shown. |
"""

CLEAN_TEST = """\
import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage


@pytest.mark.case("register-login", 1)
def test_home_page(home_page: HomePage) -> None:
    home_page.open()
    expect(home_page.title()).to_have_text("Home")
"""


def _workspace(tmp_path: Path, files: dict[str, str]) -> Path:
    for relative, text in files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


def _findings(
    tmp_path: Path,
    files: dict[str, str],
    case_text: str = CASE,
) -> tuple[QualityRule, ...]:
    workspace = _workspace(tmp_path, files)
    return tuple(
        finding.rule
        for finding in quality_findings("register-login", case_text, list(files), workspace)
    )


def test_clean_generated_test_has_no_findings(tmp_path: Path) -> None:
    assert _findings(tmp_path, {"tests/test_home.py": CLEAN_TEST}) == ()


def test_page_object_without_tests_is_ignored(tmp_path: Path) -> None:
    page_object = """\
from playwright.sync_api import Page


class HomePage:
    def __init__(self, page: Page) -> None:
        self.page = page
"""

    findings = _findings(
        tmp_path,
        {"tests/test_home.py": CLEAN_TEST, "pages/home_page.py": page_object},
    )

    assert findings == ()


def test_missing_case_is_a_finding(tmp_path: Path) -> None:
    case_text = CASE + "\n## Case 2: Account / Login\n"
    findings = _findings(
        tmp_path,
        {"tests/test_home.py": CLEAN_TEST},
        case_text=case_text,
    )

    assert findings == (QualityRule.CASE_COVERAGE,)


def test_marker_for_an_unknown_case_is_a_finding(tmp_path: Path) -> None:
    source = CLEAN_TEST.replace(
        '@pytest.mark.case("register-login", 1)',
        '@pytest.mark.case("register-login", 9)',
    )

    assert _findings(tmp_path, {"tests/test_home.py": source}) == (
        QualityRule.CASE_MARKER,
        QualityRule.CASE_COVERAGE,
    )


def test_marker_with_the_wrong_file_id_is_a_finding(tmp_path: Path) -> None:
    source = CLEAN_TEST.replace(
        '@pytest.mark.case("register-login", 1)',
        '@pytest.mark.case("other-case", 1)',
    )

    assert _findings(tmp_path, {"tests/test_home.py": source}) == (
        QualityRule.CASE_MARKER,
        QualityRule.CASE_COVERAGE,
    )


def test_test_without_a_case_marker_is_a_finding(tmp_path: Path) -> None:
    source = CLEAN_TEST.replace('@pytest.mark.case("register-login", 1)\n', "")

    assert _findings(tmp_path, {"tests/test_home.py": source}) == (
        QualityRule.CASE_MARKER,
        QualityRule.CASE_COVERAGE,
    )


def test_non_case_decorator_is_ignored(tmp_path: Path) -> None:
    source = CLEAN_TEST.replace(
        '@pytest.mark.case("register-login", 1)',
        '@pytest.mark.usefixtures("block_ads")\n@pytest.mark.case("register-login", 1)',
    )

    assert _findings(tmp_path, {"tests/test_home.py": source}) == ()


def test_mark_alias_is_not_recognized(tmp_path: Path) -> None:
    source = CLEAN_TEST.replace("import pytest", "from pytest import mark").replace(
        "@pytest.mark.case", "@mark.case"
    )

    assert _findings(tmp_path, {"tests/test_home.py": source}) == (
        QualityRule.CASE_MARKER,
        QualityRule.CASE_COVERAGE,
    )


@pytest.mark.parametrize(
    "decorator",
    [
        '@pytest.mark.case("register-login")',
        '@pytest.mark.case("register-login", CASE_NUMBER)',
        '@pytest.mark.case("register-login", True)',
    ],
)
def test_malformed_case_marker_is_treated_as_missing(tmp_path: Path, decorator: str) -> None:
    source = CLEAN_TEST.replace('@pytest.mark.case("register-login", 1)', decorator)

    assert _findings(tmp_path, {"tests/test_home.py": source}) == (
        QualityRule.CASE_MARKER,
        QualityRule.CASE_COVERAGE,
    )


def test_test_without_an_assertion_is_a_finding(tmp_path: Path) -> None:
    source = """\
import pytest

from pages.home_page import HomePage


@pytest.mark.case("register-login", 1)
def test_home_page(home_page: HomePage) -> None:
    home_page.open()
"""

    assert _findings(tmp_path, {"tests/test_home.py": source}) == (QualityRule.ASSERTION,)


@pytest.mark.parametrize(
    "line",
    [
        '    page.goto("https://automationexercise.com")',
        '    page.locator("#submit").click()',
        '    page.get_by_role("button", name="Submit").click()',
    ],
)
def test_direct_page_selectors_are_findings(tmp_path: Path, line: str) -> None:
    source = """\
import pytest

from pages.home_page import HomePage


@pytest.mark.case("register-login", 1)
def test_home_page(page: object) -> None:
    assert home_page is not None
"""

    source = source.replace("    assert home_page is not None", line + "\n    assert True")

    assert _findings(tmp_path, {"tests/test_home.py": source}) == (QualityRule.PAGE_OBJECT,)


def test_reaching_through_a_page_objects_page_is_a_finding(tmp_path: Path) -> None:
    source = CLEAN_TEST.replace(
        "    home_page.open()",
        '    home_page.page.locator("#submit").click()',
    )

    assert _findings(tmp_path, {"tests/test_home.py": source}) == (QualityRule.PAGE_OBJECT,)


def test_page_on_and_wait_are_allowed(tmp_path: Path) -> None:
    source = CLEAN_TEST.replace(
        "    home_page.open()",
        '    page.on("dialog", lambda dialog: dialog.accept())\n'
        '    page.wait_for_load_state("networkidle")\n'
        "    home_page.open()",
    ).replace("home_page: HomePage", "home_page: HomePage, page: object")

    assert _findings(tmp_path, {"tests/test_home.py": source}) == ()


def test_generated_test_outside_tests_is_a_finding(tmp_path: Path) -> None:
    assert _findings(tmp_path, {"pages/test_home.py": CLEAN_TEST}) == (QualityRule.TESTS_LOCATION,)


@pytest.mark.parametrize(
    "import_line",
    [
        "import pages.home_page",
        "from components.header import Header",
    ],
)
def test_page_object_import_forms_are_allowed(tmp_path: Path, import_line: str) -> None:
    source = CLEAN_TEST.replace("from pages.home_page import HomePage", import_line)

    assert _findings(tmp_path, {"tests/test_home.py": source}) == ()


def test_generated_test_must_import_page_objects(tmp_path: Path) -> None:
    source = CLEAN_TEST.replace("from pages.home_page import HomePage\n", "")

    assert _findings(tmp_path, {"tests/test_home.py": source}) == (QualityRule.PAGE_OBJECT_IMPORT,)


def test_unparseable_file_is_a_finding(tmp_path: Path) -> None:
    assert _findings(tmp_path, {"tests/test_broken.py": "def test_broken(:\n"}) == (
        QualityRule.SYNTAX,
        QualityRule.CASE_COVERAGE,
    )


def test_deleted_path_is_skipped(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, {"tests/test_home.py": CLEAN_TEST})

    findings = quality_findings(
        "register-login",
        CASE,
        ["tests/test_home.py", "tests/test_deleted.py"],
        workspace,
    )

    assert findings == ()
