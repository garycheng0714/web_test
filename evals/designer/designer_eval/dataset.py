"""Read a judge dataset: the labeled claims and the PRD they are judged against."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from evals.designer.designer_eval.requirements import parse_requirements
from web_test.paths import PRD_PATH
from web_test.planning.review.parser import parse_test_case


class LabeledClaim(BaseModel):
    """One fixture row. Boundary data, so a mistyped label fails here, not silently in `score`.

    The requirement text is not stored: it is read from the dataset's PRD by id, so editing the
    PRD never leaves a row holding stale text.
    """

    source_run: str
    claim_id: str
    requirement_id: str
    case_id: str
    case_markdown: str
    human_label: Literal["pass", "fail"]
    human_mode: str | None = None
    human_reason: str | None = None


@dataclass(frozen=True)
class ClaimDataset:
    """One dataset's PRD text and the labels already checked against it."""

    prd_text: str
    claims: list[LabeledClaim]


def requirement_count(case_markdown: str) -> int:
    """How many requirements the case's own yaml claims. Derived, so it cannot drift."""
    # shortcut: unparseable markdown counts as unknown (0) so a hand-written row still runs.
    # Tighten when a dataset without the rendered `## Case N:` heading appears.
    try:
        return len(parse_test_case(case_markdown, "").cases[0].requirement_ids)
    except ValueError:
        return 0


# A dataset named after the working PRD's directory tracks that PRD and has no `prd.md` of its own.
WORKING_PRD_DATASETS = {PRD_PATH.parent.name: PRD_PATH}


def dataset_prd(data_dir: Path) -> Path:
    """The PRD the dataset's labels are judged against.

    The working dataset reads the repo's PRD, so the two cannot drift. Every other dataset keeps
    its own point-in-time `prd.md` snapshot.
    """
    return WORKING_PRD_DATASETS.get(data_dir.name, data_dir / "prd.md")


def load_dataset(data_dir: Path, *, single_fr_only: bool = True) -> ClaimDataset:
    """Read a dataset. Multi-FR rows are legacy shapes, so they are excluded by default."""
    prd_text = dataset_prd(data_dir).read_text(encoding="utf-8")
    requirement_ids = {requirement.id for requirement in parse_requirements(prd_text)}
    claims: list[LabeledClaim] = []
    for line in (data_dir / "claims.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        claim = LabeledClaim.model_validate_json(line)
        if single_fr_only and requirement_count(claim.case_markdown) > 1:
            continue
        if claim.requirement_id not in requirement_ids:
            raise ValueError(
                f"{claim.claim_id} claims {claim.requirement_id}, "
                f"which {dataset_prd(data_dir).name} does not define"
            )
        claims.append(claim)
    return ClaimDataset(prd_text=prd_text, claims=claims)
