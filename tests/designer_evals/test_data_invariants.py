"""Invariants the committed judge datasets must keep.

Each check here answers a failure that cost rework once: a dataset pointing at a requirement the
PRD had removed, a dataset PRD drifting from the working PRD, and rows that no longer matched the
requirements they are judged against.
"""

import re
from pathlib import Path

import pytest

from evals.designer.designer_eval.judge import LabeledClaim
from evals.designer.designer_eval.requirements import parse_requirements
from web_test.paths import REPO_ROOT

DATA_DIR = REPO_ROOT / "evals" / "designer" / "judge" / "data"
DATASETS = sorted(path for path in DATA_DIR.iterdir() if path.is_dir())

# A dataset listed here tracks the working PRD and must be re-synced with it. The others are
# point-in-time snapshots whose rows were judged against that snapshot.
WORKING_PRD = {"automationexercise": REPO_ROOT / ".scratch" / "automationexercise" / "prd.md"}


def _dataset_id(path: Path) -> str:
    return path.name


def _rows(dataset: Path) -> list[LabeledClaim]:
    lines = (dataset / "claims.jsonl").read_text(encoding="utf-8").splitlines()
    return [LabeledClaim.model_validate_json(line) for line in lines if line.strip()]


@pytest.mark.parametrize("dataset", DATASETS, ids=_dataset_id)
def test_dataset_files_exist(dataset: Path):
    assert (dataset / "prd.md").is_file()
    assert (dataset / "claims.jsonl").is_file()


@pytest.mark.parametrize("dataset", DATASETS, ids=_dataset_id)
def test_every_claim_points_at_a_requirement_in_the_dataset_prd(dataset: Path):
    requirements = {
        requirement.id: requirement
        for requirement in parse_requirements((dataset / "prd.md").read_text(encoding="utf-8"))
    }

    unknown = sorted({row.requirement_id for row in _rows(dataset)} - set(requirements))

    assert unknown == [], f"{dataset.name} claims requirements its PRD does not define: {unknown}"


@pytest.mark.parametrize("dataset", DATASETS, ids=_dataset_id)
def test_every_requirement_has_an_acceptance_criterion(dataset: Path):
    requirements = parse_requirements((dataset / "prd.md").read_text(encoding="utf-8"))

    without = [
        requirement.id for requirement in requirements if not requirement.acceptance_criteria
    ]

    assert without == [], f"{dataset.name} requirements without an AC: {without}"


@pytest.mark.parametrize("dataset", DATASETS, ids=_dataset_id)
def test_every_claim_text_carries_the_current_ac_numbers(dataset: Path):
    requirements = {
        requirement.id: requirement
        for requirement in parse_requirements((dataset / "prd.md").read_text(encoding="utf-8"))
    }

    stale = []
    for row in _rows(dataset):
        expected = {str(ac.index) for ac in requirements[row.requirement_id].acceptance_criteria}
        found = set(re.findall(r"\*\*AC-(\d+)\*\*", row.requirement_text))
        if found != expected:
            stale.append((row.claim_id, sorted(found), sorted(expected)))

    assert stale == [], f"{dataset.name} rows did not follow their PRD's AC numbers: {stale}"


@pytest.mark.parametrize("dataset", DATASETS, ids=_dataset_id)
def test_a_claim_id_is_unique_within_its_source_run(dataset: Path):
    keys = [(row.source_run, row.claim_id) for row in _rows(dataset)]

    assert len(keys) == len(set(keys)), f"{dataset.name} repeats a claim id inside one run"


@pytest.mark.parametrize("dataset", sorted(WORKING_PRD), ids=str)
def test_dataset_prd_matches_the_working_prd(dataset: str):
    committed = (DATA_DIR / dataset / "prd.md").read_text(encoding="utf-8")
    working = WORKING_PRD[dataset].read_text(encoding="utf-8")

    assert committed == working, (
        f"{dataset}/prd.md drifted from {WORKING_PRD[dataset].relative_to(REPO_ROOT)}; "
        "copy the PRD and refresh every row's requirement_text"
    )
