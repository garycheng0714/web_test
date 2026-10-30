import pytest

from verify_helpers import case_text
from web_test.planning.verify.key import InvalidTestCase, cache_key


def test_cache_key_is_stable_and_sensitive() -> None:
    text = case_text()

    first = cache_key(text, "# PRD")
    second = cache_key(text, "# PRD")
    assert first == second

    assert cache_key(text + "\n", "# PRD") != first
    assert cache_key(text, "# PRD v2") != first


def test_cache_key_includes_the_question_set_version(monkeypatch) -> None:
    text = case_text()
    monkeypatch.setattr(
        "web_test.planning.verify.key.question_set_version",
        lambda questions: "v1",
    )
    first = cache_key(text, "# PRD")

    monkeypatch.setattr(
        "web_test.planning.verify.key.question_set_version",
        lambda questions: "v2",
    )
    second = cache_key(text, "# PRD")

    assert first != second


def test_invalid_test_case_raises() -> None:
    with pytest.raises(InvalidTestCase, match="no '## Case N' sections"):
        cache_key("---\nid: demo\n---\n\n# Demo\n", "# PRD")


def test_cache_key_includes_the_check_set_version() -> None:
    text = case_text()

    assert cache_key(text, "# PRD", check_set_version="a") != cache_key(
        text, "# PRD", check_set_version="b"
    )
