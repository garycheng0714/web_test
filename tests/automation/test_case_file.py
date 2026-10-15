from pathlib import Path

import pytest
from pydantic import ValidationError

from web_test.automation.case_file import CaseFile

SAMPLE = """\
---
id: register-login
base_url: https://automationexercise.com
---

# Register Login
"""


def test_case_file_reads_front_matter() -> None:
    case = CaseFile.from_text(SAMPLE)

    assert case.id == "register-login"
    assert str(case.base_url) == "https://automationexercise.com/"
    assert case.requirement_ids == []
    assert case.priority == "Medium"
    assert case.test_type == "Functional"


def test_case_file_requires_id_and_base_url() -> None:
    with pytest.raises(ValidationError):
        CaseFile.from_text("---\nid: register-login\n---\n")


def test_case_file_reads_a_named_artifact(tmp_path: Path) -> None:
    directory = tmp_path / "test-case"
    directory.mkdir()
    path = directory / "test-case-register-login.md"
    path.write_text(SAMPLE, encoding="utf-8")

    case, text = CaseFile.from_path(path)

    assert case.id == "register-login"
    assert text == SAMPLE


def test_case_file_rejects_a_path_outside_the_artifact_dir(tmp_path: Path) -> None:
    path = tmp_path / "register-login.md"
    path.write_text(SAMPLE, encoding="utf-8")

    with pytest.raises(ValueError):
        CaseFile.from_path(path)


def test_case_file_rejects_a_non_prefixed_name(tmp_path: Path) -> None:
    directory = tmp_path / "test-case"
    directory.mkdir()
    path = directory / "register-login.md"
    path.write_text(SAMPLE, encoding="utf-8")

    with pytest.raises(ValueError):
        CaseFile.from_path(path)


def test_case_file_rejects_a_non_markdown_name(tmp_path: Path) -> None:
    directory = tmp_path / "test-case"
    directory.mkdir()
    path = directory / "test-case-register-login.txt"
    path.write_text(SAMPLE, encoding="utf-8")

    with pytest.raises(ValueError):
        CaseFile.from_path(path)
