from pathlib import Path

from web_test.command import CommandResult
from web_test.publishing.suite import Suite


def test_suite_keeps_the_failing_output(tmp_path: Path) -> None:
    expected = CommandResult(1, "stdout", "stderr")
    suite = Suite(lambda args, *, cwd: expected, tmp_path)

    assert suite.run() == expected
