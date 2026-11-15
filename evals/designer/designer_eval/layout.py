"""Where one designer eval keeps its runs and judge datasets."""

from pathlib import Path

from web_test.paths import REPO_ROOT

RUNS_DIR = REPO_ROOT / "evals" / "designer" / "runs"
JUDGE_DATA_DIR = REPO_ROOT / "evals" / "designer" / "judge" / "data"
JUDGE_RUNS_DIR = REPO_ROOT / "evals" / "designer" / "judge" / "runs"


def latest_run(directory: Path, marker: str) -> Path:
    """The most recent run that holds `marker`; one without it would fail later."""
    runs = [path for path in directory.iterdir() if (path / marker).is_file()]
    if not runs:
        raise FileNotFoundError(f"no run with {marker} under {directory}")
    return max(runs, key=lambda path: path.stat().st_mtime)


def resolve_run_dir(*, run: str | None, run_dir: str | None, marker: str) -> Path:
    """`--run-dir` wins, then `--run`, then the latest run that can serve this command."""
    if run_dir:
        return Path(run_dir)
    if run:
        return RUNS_DIR / run
    return latest_run(RUNS_DIR, marker)
