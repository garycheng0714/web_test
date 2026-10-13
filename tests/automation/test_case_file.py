from pathlib import Path

import pytest
from pydantic import ValidationError

from web_test.automation.case_file import CaseFile

SAMPLE = """\
---
id: test-case-0001
base_url: https://automationexercise.com
requirement_ids: [FR-CNT-01]
priority: High
test_type: Functional
---

# Test Case 6: Contact Us Form
"""


def test_case_file_reads_front_matter() -> None:
    case = CaseFile.from_text(SAMPLE)

    assert case.id == "test-case-0001"
    assert str(case.base_url) == "https://automationexercise.com/"
    assert case.requirement_ids == ["FR-CNT-01"]
    assert case.priority == "High"
    assert case.test_type == "Functional"


def test_case_file_defaults_optional_fields() -> None:
    case = CaseFile.from_text("---\nid: test-case-0002\nbase_url: https://example.com\n---\n")

    assert case.requirement_ids == []
    assert case.priority == "Medium"
    assert case.test_type == "Functional"


def test_case_file_requires_id_and_base_url() -> None:
    with pytest.raises(ValidationError):
        CaseFile.from_text("---\nid: test-case-0003\n---\n")


def test_case_file_rejects_a_non_artifact_path(tmp_path: Path) -> None:
    path = tmp_path / "test-case-0001.md"
    path.write_text(SAMPLE, encoding="utf-8")

    with pytest.raises(ValueError):
        CaseFile.from_path(path)
