from pathlib import Path

from web_test.command import CommandResult
from web_test.publishing.suite import Suite


def test_suite_keeps_the_failing_output(tmp_path: Path) -> None:
    expected = CommandResult(1, "stdout", "stderr")
    suite = Suite(lambda args, *, cwd: expected, tmp_path)

    assert suite.run() == expected


def test_suite_retains_traces_for_failures(tmp_path: Path) -> None:
    captured: list[list[str]] = []
    suite = Suite(lambda args, *, cwd: captured.append(args) or CommandResult(0), tmp_path)

    suite.run()

    assert "--tracing=retain-on-failure" in captured[0]
    assert "--output=test-results/suite" in captured[0]
