"""Parse the requirements a designer eval measures against."""

import re
from dataclasses import dataclass

_REQUIREMENT = re.compile(r"^###\s+(FR-[A-Z]+-\d+)\s*(.*)$")
_HEADING = re.compile(r"^#{2,3}\s")


@dataclass(frozen=True)
class Requirement:
    id: str
    title: str
    text: str


def parse_requirements(prd_text: str) -> list[Requirement]:
    """Extract `### FR-*` sections, stopping at the next `##` or `###` heading."""
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
