from pathlib import Path

from web_test.planning.verify.resolution import ResolutionKind, resolve
from verify_helpers import write_case, write_prd


def test_nothing_when_no_artifact_changed(tmp_path: Path) -> None:
    (tmp_path / "test-case").mkdir()
    (tmp_path / "test-case" / "notes.md").write_text("notes", encoding="utf-8")

    assert resolve([], workspace=tmp_path).kind is ResolutionKind.NOTHING
    assert (
        resolve(["test-case/notes.md", "prd/demo.md"], workspace=tmp_path).kind
        is ResolutionKind.NOTHING
    )


def test_ready_returns_the_texts(tmp_path: Path) -> None:
    case_path, case_text = write_case(tmp_path)
    write_prd(tmp_path)

    result = resolve([case_path], workspace=tmp_path)

    assert result.kind is ResolutionKind.READY
    texts = result.texts
    assert texts is not None
    assert texts.test_case_text == case_text
    assert texts.prd_text == "# PRD"


def test_multiple_artifacts_are_reported(tmp_path: Path) -> None:
    first, _ = write_case(tmp_path, "one")
    second, _ = write_case(tmp_path, "two")

    result = resolve([second, first], workspace=tmp_path)

    assert result.kind is ResolutionKind.MULTIPLE
    assert result.files == (first, second)
    assert result.texts is None


def test_missing_prd_is_reported(tmp_path: Path) -> None:
    case_path, _ = write_case(tmp_path)

    result = resolve([case_path], workspace=tmp_path)

    assert result.kind is ResolutionKind.MISSING_PRD
    assert str(tmp_path / "prd" / "demo.md") in result.detail


def test_unreadable_prd_is_invalid(tmp_path: Path, monkeypatch) -> None:
    case_path, _ = write_case(tmp_path)
    prd_path = write_prd(tmp_path)
    original_read_text = Path.read_text

    def read_text(self: Path, *args, **kwargs):
        if self == prd_path:
            raise PermissionError("denied")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)

    result = resolve([case_path], workspace=tmp_path)

    assert result.kind is ResolutionKind.INVALID
    assert "reading PRD" in result.detail
    assert str(prd_path) in result.detail


def test_a_prd_that_disappears_during_read_is_missing(
    tmp_path: Path, monkeypatch
) -> None:
    case_path, _ = write_case(tmp_path)
    prd_path = write_prd(tmp_path)
    original_read_text = Path.read_text

    def read_text(self: Path, *args, **kwargs):
        if self == prd_path:
            raise FileNotFoundError(f"{prd_path} disappeared")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)

    result = resolve([case_path], workspace=tmp_path)

    assert result.kind is ResolutionKind.MISSING_PRD
    assert str(prd_path) in result.detail


def test_missing_front_matter_is_invalid(tmp_path: Path) -> None:
    path = tmp_path / "test-case" / "test-case-demo.md"
    path.parent.mkdir()
    path.write_text("# Demo\n", encoding="utf-8")
    write_prd(tmp_path)

    result = resolve(["test-case/test-case-demo.md"], workspace=tmp_path)

    assert result.kind is ResolutionKind.INVALID
    assert "missing front matter" in result.detail


def test_a_missing_front_matter_id_is_invalid(tmp_path: Path) -> None:
    path = tmp_path / "test-case" / "test-case-demo.md"
    path.parent.mkdir()
    path.write_text("---\nbase_url: https://example.com\n---\n", encoding="utf-8")
    write_prd(tmp_path)

    result = resolve(["test-case/test-case-demo.md"], workspace=tmp_path)

    assert result.kind is ResolutionKind.INVALID
    assert "string id" in result.detail
