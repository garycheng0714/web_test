from pathlib import Path

from verify_helpers import write_case, write_prd
from web_test.planning.verify.prepare import prepare
from web_test.planning.verify.resolution import ResolutionKind


def test_prepare_builds_aready_input(tmp_path: Path) -> None:
    case_path, case_text = write_case(tmp_path)
    write_prd(tmp_path)

    verification_input = prepare([case_path], workspace=tmp_path)

    assert verification_input.kind is ResolutionKind.READY
    assert verification_input.cache_key is not None
    assert len(verification_input.cache_key) == 64
    assert verification_input.test_case_text == case_text
    assert verification_input.prd_text == "# PRD"


def test_prepare_builds_an_early_input(tmp_path: Path) -> None:
    verification_input = prepare([], workspace=tmp_path)

    assert verification_input.kind is ResolutionKind.NOTHING
    assert verification_input.test_case_text is None


def test_prepare_marks_a_test_case_without_cases_invalid(tmp_path: Path) -> None:
    path = tmp_path / "test-case" / "test-case-demo.md"
    path.parent.mkdir()
    path.write_text("---\nid: demo\n---\n\n# Demo\n", encoding="utf-8")
    write_prd(tmp_path)

    verification_input = prepare(["test-case/test-case-demo.md"], workspace=tmp_path)

    assert verification_input.kind is ResolutionKind.INVALID
    assert "no '## Case N' sections" in verification_input.detail
