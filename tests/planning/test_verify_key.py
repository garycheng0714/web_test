import pytest

from web_test.planning.cases_writer import render_document
from web_test.planning.schema import Case
from web_test.planning.verify_key import InvalidTestCase, cache_key


def _case() -> Case:
    return Case.model_validate(
        {
            "requirement_ids": ["FR-1"],
            "module_feature": "Account",
            "test_scenario": "Register",
            "steps": [{"action": "Go", "expected_result": "Page shown"}],
            "priority": "High",
            "severity": "Critical",
            "test_type": "Functional",
        }
    )


def _case_text() -> str:
    return render_document(
        [_case()], id="demo", base_url="https://example.com", title="Demo"
    )


def test_cache_key_is_stable_and_sensitive() -> None:
    text = _case_text()

    first = cache_key(text, "# PRD")
    second = cache_key(text, "# PRD")
    assert first == second

    assert cache_key(text + "\n", "# PRD") != first
    assert cache_key(text, "# PRD v2") != first


def test_cache_key_includes_the_question_set_version(monkeypatch) -> None:
    text = _case_text()
    monkeypatch.setattr(
        "web_test.planning.verify_key.question_set_version",
        lambda questions: "v1",
    )
    first = cache_key(text, "# PRD")

    monkeypatch.setattr(
        "web_test.planning.verify_key.question_set_version",
        lambda questions: "v2",
    )
    second = cache_key(text, "# PRD")

    assert first != second


def test_invalid_test_case_raises() -> None:
    with pytest.raises(InvalidTestCase, match="no '## Case N' sections"):
        cache_key("---\nid: demo\n---\n\n# Demo\n", "# PRD")
