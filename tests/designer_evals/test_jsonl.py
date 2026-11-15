import pytest
from pydantic import BaseModel, ValidationError

from evals.designer.designer_eval.jsonl import read_rows, write_rows


class _Row(BaseModel):
    name: str
    note: str | None = None


def test_write_rows_keeps_null_fields_and_ends_with_a_newline(tmp_path):
    path = tmp_path / "rows.jsonl"

    write_rows(path, [_Row(name="a"), _Row(name="b", note="x")])

    text = path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert '"note":null' in text
    assert read_rows(path, _Row) == [_Row(name="a"), _Row(name="b", note="x")]


def test_read_rows_skips_blank_lines(tmp_path):
    path = tmp_path / "rows.jsonl"
    path.write_text('\n{"name": "a"}\n\n\n', encoding="utf-8")

    assert read_rows(path, _Row) == [_Row(name="a")]


def test_read_rows_rejects_a_row_that_does_not_match_the_model(tmp_path):
    path = tmp_path / "rows.jsonl"
    path.write_text('{"note": "no name"}\n', encoding="utf-8")

    with pytest.raises(ValidationError):
        read_rows(path, _Row)
