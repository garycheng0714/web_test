import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from web_test.planning.schema import Case


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def title_from_stem(stem: str) -> str:
    """A human title from a PRD file stem, e.g. `register-login` → `Register Login`."""
    return " ".join(part.capitalize() for part in re.split(r"[-_]", stem) if part)


def _join(blocks: Iterable[str | None]) -> str:
    """Join the non-empty blocks with exactly one blank line between them."""
    return "\n\n".join(block for block in blocks if block)


def _heading(case: Case, index: int) -> str:
    return f"## Case {index}: {case.module_feature}: {case.test_scenario}"


def _metadata(case: Case) -> str:
    return "\n".join(
        [
            "```yaml",
            f"requirement_ids: [{', '.join(case.requirement_ids)}]",
            f"priority: {case.priority}",
            f"test_type: {case.test_type}",
            "```",
        ]
    )


def _preconditions(case: Case) -> str | None:
    if not case.preconditions:
        return None
    return "\n".join(["### Preconditions", "", *(f"- {item}" for item in case.preconditions)])


def _steps_table(case: Case) -> str:
    rows = [
        f"| {index} | {escape_cell(step.action)} | {escape_cell(step.expected_result)} |"
        for index, step in enumerate(case.steps, start=1)
    ]
    return "\n".join(
        ["### Test Steps", "", "| Step | Action | Expected Result |", "| --- | --- | --- |", *rows]
    )


def _notes(case: Case) -> str | None:
    if not case.notes:
        return None
    return f"### Notes\n\n{case.notes}"


def _open_questions(questions: Iterable[str]) -> str | None:
    if not questions:
        return None
    return "\n".join(["## Open Questions", "", *(f"- {question}" for question in questions)])


def render_case_section(case: Case, *, index: int) -> str:
    """Render one case as a `## Case N` section with a machine-readable metadata block."""
    return _join(
        [
            _heading(case, index),
            _metadata(case),
            f"**Severity:** {case.severity}",
            _preconditions(case),
            _steps_table(case),
            _notes(case),
        ]
    )


def render_document(
    cases: list[Case], *, id: str, base_url: str, title: str, open_questions: Iterable[str] = ()
) -> str:
    """Render one test-case file: front-matter, a title, one section per case, and open questions."""
    front_matter = f"---\nid: {id}\nbase_url: {base_url}\n---"
    sections = (render_case_section(case, index=index) for index, case in enumerate(cases, start=1))
    return _join([front_matter, f"# {title}", *sections, _open_questions(open_questions)]) + "\n"


@dataclass(frozen=True)
class CaseWriter:
    """Writes a PRD's cases into one `test-case/test-case-<prd-stem>.md` file (overwriting any existing one)."""

    directory: Path
    base_url: str

    def write(
        self,
        prd_stem: str,
        cases: list[Case],
        open_questions: Iterable[str] = (),
        *,
        content: str | None = None,
    ) -> str:
        """Write the PRD's file (rendering it when no content is supplied); return the file name."""
        self.directory.mkdir(parents=True, exist_ok=True)
        name = f"test-case-{prd_stem}.md"
        if content is None:
            content = render_document(
                cases,
                id=prd_stem,
                base_url=self.base_url,
                title=title_from_stem(prd_stem),
                open_questions=open_questions,
            )
        (self.directory / name).write_text(content, encoding="utf-8")
        return name
