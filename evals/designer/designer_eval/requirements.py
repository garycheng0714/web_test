"""Parse the requirements a designer eval measures against."""

import re
from dataclasses import dataclass, field

_REQUIREMENT = re.compile(r"^#{3,4}\s+(FR-[A-Z]+-\d+)\s*(.*)$")
_HEADING = re.compile(r"^#{2,4}\s")
_ACCEPTANCE_CRITERION = re.compile(r"^- \*\*AC-(\d+)\*\*[:\uff1a]\s*(.*)$")


@dataclass(frozen=True)
class AcceptanceCriterion:
    id: str
    index: int
    text: str


@dataclass(frozen=True)
class Requirement:
    id: str
    title: str
    text: str
    acceptance_criteria: list[AcceptanceCriterion] = field(default_factory=list)


def _acceptance_criteria(requirement_id: str, lines: list[str]) -> list[AcceptanceCriterion]:
    """Read the `- **AC-N**: ...` bullets of one requirement.

    The author writes the number, so inserting a criterion does not renumber the ones after it.
    """
    criteria: list[AcceptanceCriterion] = []
    current: tuple[int, list[str]] | None = None

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        index, parts = current
        criteria.append(
            AcceptanceCriterion(
                id=f"{requirement_id}-AC{index}",
                index=index,
                text=" ".join(part for part in parts if part).strip(),
            )
        )
        current = None

    for line in lines:
        match = _ACCEPTANCE_CRITERION.match(line)
        if match:
            flush()
            current = (int(match.group(1)), [match.group(2).strip()])
            continue
        if current is not None and line.startswith("  ") and line.strip():
            current[1].append(line.strip())
            continue
        flush()
    flush()

    indexes = [criterion.index for criterion in criteria]
    duplicates = sorted({index for index in indexes if indexes.count(index) > 1})
    if duplicates:
        raise ValueError(f"{requirement_id} repeats acceptance criterion numbers {duplicates}")
    return criteria


def parse_requirements(prd_text: str) -> list[Requirement]:
    """Extract `###`/`####` FR-* sections, stopping at the next `##`-`####` heading."""
    requirements: list[Requirement] = []
    current_id: str | None = None
    current_title = ""
    lines: list[str] = []

    def flush() -> None:
        nonlocal current_id, current_title, lines
        if current_id is not None:
            requirements.append(
                Requirement(
                    id=current_id,
                    title=current_title,
                    text="\n".join(lines).strip(),
                    acceptance_criteria=_acceptance_criteria(current_id, lines),
                )
            )
        current_id = None
        current_title = ""
        lines = []

    for line in prd_text.splitlines():
        match = _REQUIREMENT.match(line)
        if match:
            flush()
            current_id = match.group(1)
            current_title = match.group(2).strip()
            lines = [line]
            continue
        if current_id is not None and _HEADING.match(line):
            flush()
            continue
        if current_id is not None:
            lines.append(line)

    flush()
    if not requirements:
        raise ValueError("no FR-* requirements found in PRD")
    return requirements
