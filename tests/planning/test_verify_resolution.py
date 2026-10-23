from pathlib import Path

from web_test.planning.cases_writer import render_document
from web_test.planning.schema import Case
from web_test.planning.verify.resolution import ResolutionKind, resolve

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


def _write_case(
    root: Path, case_id: str = "demo", *, title: str = "Demo"
) -> tuple[str, str]:
    text = render_document(
        [_case()], id=case_id, base_url="https://example.com", title=title
    )
    path = root / "test-case" / f"test-case-{case_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return f"test-case/test-case-{case_id}.md", text


def _write_prd(root: Path, case_id: str = "demo", text: str = "# PRD") -> Path:
    path = root / "prd" / f"{case_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_nothing_when_no_artifact_changed(tmp_path: Path) -> None:
    (tmp_path / "test-case").mkdir()
    (tmp_path / "test-case" / "notes.md").write_text("notes", encoding="utf-8")

    assert resolve([], workspace=tmp_path).kind is ResolutionKind.NOTHING
    assert (
        resolve(["test-case/notes.md", "prd/demo.md"], workspace=tmp_path).kind
        is ResolutionKind.NOTHING
    )


def test_ready_returns_the_texts(tmp_path: Path) -> None:
    case_path, case_text = _write_case(tmp_path)
    _write_prd(tmp_path)

    result = resolve([case_path], workspace=tmp_path)

    assert result.kind is ResolutionKind.READY
    texts = result.texts
    assert texts is not None
    assert texts.test_case_text == case_text
    assert texts.prd_text == "# PRD"


def test_multiple_artifacts_are_reported(tmp_path: Path) -> None:
    first, _ = _write_case(tmp_path, "one")
    second, _ = _write_case(tmp_path, "two")

    result = resolve([second, first], workspace=tmp_path)

    assert result.kind is ResolutionKind.MULTIPLE
    assert result.files == (first, second)
    assert result.texts is None


def test_missing_prd_is_reported(tmp_path: Path) -> None:
    case_path, _ = _write_case(tmp_path)

    result = resolve([case_path], workspace=tmp_path)

    assert result.kind is ResolutionKind.MISSING_PRD
    assert str(tmp_path / "prd" / "demo.md") in result.detail


def test_unreadable_prd_is_invalid(tmp_path: Path, monkeypatch) -> None:
    case_path, _ = _write_case(tmp_path)
    prd_path = _write_prd(tmp_path)
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
    case_path, _ = _write_case(tmp_path)
    prd_path = _write_prd(tmp_path)
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
    _write_prd(tmp_path)

    result = resolve(["test-case/test-case-demo.md"], workspace=tmp_path)

    assert result.kind is ResolutionKind.INVALID
    assert "missing front matter" in result.detail


def test_a_missing_front_matter_id_is_invalid(tmp_path: Path) -> None:
    path = tmp_path / "test-case" / "test-case-demo.md"
    path.parent.mkdir()
    path.write_text("---\nbase_url: https://example.com\n---\n", encoding="utf-8")
    _write_prd(tmp_path)

    result = resolve(["test-case/test-case-demo.md"], workspace=tmp_path)

    assert result.kind is ResolutionKind.INVALID
    assert "string id" in result.detail
