from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel

from web_test.planning.review.jev import JEV_MODEL
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.questions import (
    question_set_version,
    questions_for_subject,
)
from web_test.planning.review.record import DEFAULT_BANDS
from web_test.planning.review.verification import digest_text


class ResolutionKind(StrEnum):
    """How resolving the changed paths ended."""

    READY = "ready"
    NOTHING = "nothing"
    MULTIPLE = "multiple"
    MISSING_PRD = "missing_prd"
    INVALID = "invalid"


class TestCaseInput(BaseModel):
    """The raw Test Case artifact a verdict is bound to."""

    path: Path
    id: str
    text: str
    digest: str


class PrdInput(BaseModel):
    """The raw PRD a verdict is bound to."""

    path: Path
    text: str
    digest: str


class VerificationData(BaseModel):
    """The raw artifacts and binding a verdict is computed from."""

    test_case: TestCaseInput
    prd: PrdInput
    question_set_version: str
    cache_key: str


@dataclass(frozen=True)
class Resolution:
    """The result of resolving the changed paths."""

    kind: ResolutionKind
    files: tuple[str, ...] = ()
    detail: str = ""
    verdict_input: VerificationData | None = None


# shortcut: mirrors automation.case_file's artifact shape; share if a third caller appears.
def _is_artifact(path: Path) -> bool:
    return (
        path.parent.name == "test-case"
        and path.name.startswith("test-case-")
        and path.suffix == ".md"
    )


def _front_matter_id(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing front matter")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            break
    else:
        raise ValueError("unterminated front matter")
    data = yaml.safe_load("\n".join(lines[1:index])) or {}
    case_id = data.get("id") if isinstance(data, dict) else None
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("front matter needs a string id")
    return case_id


def _read_case(workspace: Path, case_path: Path) -> TestCaseInput:
    case_file = case_path if case_path.is_absolute() else workspace / case_path
    text = case_file.read_text(encoding="utf-8")
    return TestCaseInput(
        path=case_path,
        id=_front_matter_id(text),
        text=text,
        digest=digest_text(text),
    )


def _read_prd(workspace: Path, case_id: str) -> PrdInput:
    path = workspace / "prd" / f"{case_id}.md"
    if not path.is_file():
        raise FileNotFoundError(f"{path} does not exist")
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise
    except OSError as error:
        raise ValueError(f"reading PRD {path} failed: {error}") from error
    return PrdInput(path=path, text=text, digest=digest_text(text))


def _cache_key(test_case_digest: str, prd_digest: str, version: str) -> str:
    payload = "\n".join(
        [
            test_case_digest,
            prd_digest,
            version,
            JEV_MODEL,
            str(DEFAULT_BANDS.pass_min),
            str(DEFAULT_BANDS.needs_review_min),
        ]
    )
    return digest_text(payload)


def resolve(changed_paths: Iterable[str], *, workspace: Path) -> Resolution:
    """Resolve the changed paths to the single Test Case file and its inputs."""
    artifacts = sorted(
        path for path in (Path(raw) for raw in changed_paths) if _is_artifact(path)
    )
    if not artifacts:
        return Resolution(ResolutionKind.NOTHING)
    if len(artifacts) > 1:
        return Resolution(ResolutionKind.MULTIPLE, files=tuple(str(path) for path in artifacts))

    case_path = artifacts[0]
    try:
        test_case = _read_case(workspace, case_path)
    except (OSError, ValueError) as error:
        return Resolution(ResolutionKind.INVALID, detail=str(error))

    try:
        prd = _read_prd(workspace, test_case.id)
    except FileNotFoundError as error:
        return Resolution(ResolutionKind.MISSING_PRD, detail=str(error))
    except ValueError as error:
        return Resolution(ResolutionKind.INVALID, detail=str(error))

    try:
        subject = parse_test_case(test_case.text, prd.text)
    except (ValueError, yaml.YAMLError) as error:
        return Resolution(ResolutionKind.INVALID, detail=str(error))

    version = question_set_version(questions_for_subject(subject))
    return Resolution(
        ResolutionKind.READY,
        verdict_input=VerificationData(
            test_case=test_case,
            prd=prd,
            question_set_version=version,
            cache_key=_cache_key(test_case.digest, prd.digest, version),
        ),
    )
