"""Invariants the committed judge datasets must keep.

Each check here answers a failure that cost rework once: a dataset pointing at a requirement the
PRD had removed, and a dataset whose rows no longer resolved against the PRD they are judged with.
The PRD itself is not copied into the working dataset (`judge.dataset_prd`), so it cannot drift.
"""

from pathlib import Path

import pytest

from evals.designer.designer_eval.judge import LabeledClaim, dataset_prd
from evals.designer.designer_eval.requirements import parse_requirements
from web_test.paths import REPO_ROOT

DATA_DIR = REPO_ROOT / "evals" / "designer" / "judge" / "data"
DATASETS = sorted(path for path in DATA_DIR.iterdir() if path.is_dir())


def _dataset_id(path: Path) -> str:
    return path.name


def _rows(dataset: Path) -> list[LabeledClaim]:
    lines = (dataset / "claims.jsonl").read_text(encoding="utf-8").splitlines()
    return [LabeledClaim.model_validate_json(line) for line in lines if line.strip()]


@pytest.mark.parametrize("dataset", DATASETS, ids=_dataset_id)
def test_dataset_files_exist(dataset: Path):
    assert dataset_prd(dataset).is_file()
    assert (dataset / "claims.jsonl").is_file()


@pytest.mark.parametrize("dataset", DATASETS, ids=_dataset_id)
def test_every_claim_points_at_a_requirement_in_the_dataset_prd(dataset: Path):
    requirements = {
        requirement.id: requirement
        for requirement in parse_requirements(dataset_prd(dataset).read_text(encoding="utf-8"))
    }

    unknown = sorted({row.requirement_id for row in _rows(dataset)} - set(requirements))

    assert unknown == [], f"{dataset.name} claims requirements its PRD does not define: {unknown}"


@pytest.mark.parametrize("dataset", DATASETS, ids=_dataset_id)
def test_a_claim_id_is_unique_within_its_source_run(dataset: Path):
    keys = [(row.source_run, row.claim_id) for row in _rows(dataset)]

    assert len(keys) == len(set(keys)), f"{dataset.name} repeats a claim id inside one run"
