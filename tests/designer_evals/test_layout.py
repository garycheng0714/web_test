import os
from pathlib import Path

import pytest

from evals.designer.designer_eval import layout


def _run(directory: Path, name: str, *, marker: str, mtime: int) -> Path:
    path = directory / name
    path.mkdir()
    (path / marker).write_text("", encoding="utf-8")
    os.utime(path, (mtime, mtime))
    return path


def test_latest_run_picks_the_newest_directory_that_holds_the_marker(tmp_path: Path):
    older = _run(tmp_path, "run-1", marker="run.json", mtime=1_000)
    newer = _run(tmp_path, "run-2", marker="run.json", mtime=2_000)
    exported = tmp_path / "exported"
    exported.mkdir()
    (exported / "labels.jsonl").write_text("", encoding="utf-8")

    assert layout.latest_run(tmp_path, "run.json") == newer
    assert layout.latest_run(tmp_path, "labels.jsonl") == exported
    assert older.exists()


def test_latest_run_names_the_marker_when_nothing_matches(tmp_path: Path):
    (tmp_path / "run-1").mkdir()

    with pytest.raises(FileNotFoundError, match=r"run\.json"):
        layout.latest_run(tmp_path, "run.json")


def test_resolve_run_dir_prefers_the_explicit_dir_then_the_run_name(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(layout, "RUNS_DIR", tmp_path)

    explicit = layout.resolve_run_dir(run="run-2", run_dir="/somewhere/else", marker="run.json")
    named = layout.resolve_run_dir(run="run-2", run_dir=None, marker="run.json")

    assert explicit == Path("/somewhere/else")
    assert named == tmp_path / "run-2"


def test_resolve_run_dir_falls_back_to_the_latest_run(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(layout, "RUNS_DIR", tmp_path)
    newest = _run(tmp_path, "run-2", marker="labels.jsonl", mtime=2_000)
    _run(tmp_path, "run-1", marker="run.json", mtime=1_000)

    assert layout.resolve_run_dir(run=None, run_dir=None, marker="labels.jsonl") == newest
