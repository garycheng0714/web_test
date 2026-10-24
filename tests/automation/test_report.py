from pathlib import Path

from web_test.automation.report import (
    TestStatus,
    build_run_report,
    parse_junit,
    read_junit,
    render_run_report,
)

JUNIT = """\
<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite name="pytest tests">
    <testcase classname="tests.test_home" name="test_home_page" file="tests/test_home.py" line="1" time="0.001" />
    <testcase classname="tests.test_home" name="test_broken" file="tests/test_home.py" line="5" time="0.001">
      <failure message="expected 1&#10;got 2">traceback</failure>
    </testcase>
    <testcase classname="tests.test_home" name="test_skipped" file="tests/test_home.py" line="9" time="0">
      <skipped message="not today" />
    </testcase>
    <testcase classname="tests.test_existing" name="test_old" file="tests/test_existing.py" line="1" time="0.001" />
    <testcase classname="tests.test_existing" name="test_old_fail" file="tests/test_existing.py" line="5" time="0.001">
      <failure message="old failed">traceback</failure>
    </testcase>
    <testcase classname="tests.test_existing" name="test_old_skip" file="tests/test_existing.py" line="9" time="0">
      <skipped message="skip" />
    </testcase>
    <testcase classname="tests.test_existing.TestClass" name="test_class_fail" file="tests/test_existing.py" line="20" time="0.001">
      <error message="setup exploded">traceback</error>
    </testcase>
  </testsuite>
</testsuites>
"""


def test_parse_junit_reads_status_and_message() -> None:
    outcomes = {outcome.nodeid: outcome for outcome in parse_junit(JUNIT)}

    assert outcomes["tests.test_home::test_home_page"].status is TestStatus.PASSED
    assert outcomes["tests.test_home::test_broken"].status is TestStatus.FAILED
    assert outcomes["tests.test_home::test_broken"].message == "expected 1"
    assert outcomes["tests.test_home::test_skipped"].status is TestStatus.SKIPPED
    assert outcomes["tests.test_existing.TestClass::test_class_fail"].status is TestStatus.FAILED
    assert outcomes["tests.test_existing.TestClass::test_class_fail"].message == "setup exploded"


def test_build_run_report_classifies_generated_and_existing() -> None:
    outcomes = parse_junit(JUNIT)

    report = build_run_report(outcomes, ["tests/test_home.py", "pages/home_page.py"])

    assert report.junit_available
    assert {outcome.nodeid for outcome in report.generated} == {
        "tests.test_home::test_home_page",
        "tests.test_home::test_broken",
        "tests.test_home::test_skipped",
    }
    assert {outcome.nodeid for outcome in report.failing} == {
        "tests.test_existing::test_old_fail",
        "tests.test_existing.TestClass::test_class_fail",
    }


def test_build_run_report_without_junit() -> None:
    report = build_run_report(None, ["tests/test_home.py"])

    assert not report.junit_available
    assert report.generated == ()
    assert report.failing == ()


def test_read_junit_returns_none_for_a_missing_file(tmp_path: Path) -> None:
    assert read_junit(tmp_path / "missing.xml") is None


def test_read_junit_returns_none_for_malformed_xml(tmp_path: Path) -> None:
    path = tmp_path / "junit.xml"
    path.write_text("<testsuites>", encoding="utf-8")

    assert read_junit(path) is None


def test_render_run_report_lists_generated_and_failing_existing() -> None:
    report = build_run_report(parse_junit(JUNIT), ["tests/test_home.py"])

    text = render_run_report(report)

    assert "## Run report" in text
    assert "### Generated tests" in text
    assert "- `PASSED` tests.test_home::test_home_page" in text
    assert "- `FAILED` tests.test_home::test_broken — expected 1" in text
    assert "- `SKIPPED` tests.test_home::test_skipped" in text
    assert "### Failing existing tests" in text
    assert "- `FAILED` tests.test_existing::test_old_fail — old failed" in text
    assert "- `PASSED` tests.test_existing::test_old" not in text
    assert "- `SKIPPED` tests.test_existing::test_old_skip" not in text


def test_render_run_report_reports_unavailable_junit() -> None:
    text = render_run_report(build_run_report(None, []))

    assert "JUnit XML was unavailable" in text


def test_failure_message_is_capped() -> None:
    long_message = "x" * 300
    text = render_run_report(
        build_run_report(
            (
                parse_junit(
                    f'<testsuites><testsuite><testcase classname="tests.test_home" '
                    f'name="test_broken" file="tests/test_home.py">'
                    f'<failure message="{long_message}" /></testcase></testsuite></testsuites>'
                )[0],
            ),
            ["tests/test_home.py"],
        )
    )

    assert long_message not in text
    assert "x" * 200 in text
