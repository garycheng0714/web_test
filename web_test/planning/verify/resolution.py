from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

import yaml


class ResolutionKind(StrEnum):
    """How resolving the changed paths ended."""

    READY = "ready"
    NOTHING = "nothing"
    MULTIPLE = "multiple"
    MISSING_PRD = "missing_prd"
    INVALID = "invalid"


@dataclass(frozen=True)
class ResolvedTexts:
    """The Test Case and PRD texts resolved from the changed paths."""

    test_case_text: str
    prd_text: str


EarlyKind = Literal[
    ResolutionKind.NOTHING,
    ResolutionKind.MULTIPLE,
    ResolutionKind.MISSING_PRD,
    ResolutionKind.INVALID,
]


@dataclass(frozen=True)
class EarlyResolution:
    """A resolution that has no Test Case and PRD texts to verify."""

    kind: EarlyKind
    files: tuple[str, ...] = ()
    detail: str = ""


@dataclass(frozen=True)
class ReadyResolution:
    """A resolved Test Case and PRD ready for a verdict."""

    texts: ResolvedTexts
    kind: Literal[ResolutionKind.READY] = ResolutionKind.READY


Resolution = ReadyResolution | EarlyResolution


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


def _read_case(workspace: Path, case_path: Path) -> tuple[str, str]:
    case_file = case_path if case_path.is_absolute() else workspace / case_path
    text = case_file.read_text(encoding="utf-8")
    return _front_matter_id(text), text


def _read_prd(workspace: Path, case_id: str) -> str:
    path = workspace / "prd" / f"{case_id}.md"
    if not path.is_file():
        raise FileNotFoundError(f"{path} does not exist")
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise
    except OSError as error:
        raise ValueError(f"reading PRD {path} failed: {error}") from error


def resolve(changed_paths: Iterable[str], *, workspace: Path) -> Resolution:
    """Resolve the changed paths to the single Test Case file and its inputs."""
    artifacts = sorted(path for path in (Path(raw) for raw in changed_paths) if _is_artifact(path))
    if not artifacts:
        return EarlyResolution(ResolutionKind.NOTHING)
    if len(artifacts) > 1:
        return EarlyResolution(
            ResolutionKind.MULTIPLE, files=tuple(str(path) for path in artifacts)
        )

    case_path = artifacts[0]
    try:
        case_id, case_text = _read_case(workspace, case_path)
    except (OSError, ValueError) as error:
        return EarlyResolution(ResolutionKind.INVALID, detail=str(error))

    try:
        prd_text = _read_prd(workspace, case_id)
    except FileNotFoundError as error:
        return EarlyResolution(ResolutionKind.MISSING_PRD, detail=str(error))
    except ValueError as error:
        return EarlyResolution(ResolutionKind.INVALID, detail=str(error))

    return ReadyResolution(
        texts=ResolvedTexts(test_case_text=case_text, prd_text=prd_text),
    )
