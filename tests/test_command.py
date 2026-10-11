import pytest

from web_test.command import CommandResult


def test_check_passes_on_success() -> None:
    result = CommandResult(0, stdout="ok")

    assert result.check() is result


def test_check_raises_with_stderr() -> None:
    with pytest.raises(RuntimeError, match="boom"):
        CommandResult(1, stderr="boom").check()


def test_check_falls_back_when_stderr_is_empty() -> None:
    with pytest.raises(RuntimeError, match="exit 2"):
        CommandResult(2).check()
