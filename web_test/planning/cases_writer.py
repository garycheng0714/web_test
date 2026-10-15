import re
from dataclasses import dataclass
from pathlib import Path

from web_test.planning.schema import Case

_ID = re.compile(r"test-case-(\d+)\.md$")


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_case(case: Case, *, id: str, base_url: str) -> str:
    """Render one test-case file in the `test-case/test-case-<id>.md` format."""
    requirement_ids = ", ".join(case.requirement_ids)
    lines = [
        "---",
        f"id: {id}",
        f"base_url: {base_url}",
        f"requirement_ids: [{requirement_ids}]",
        f"priority: {case.priority}",
        f"test_type: {case.test_type}",
        "---",
        "",
        f"# {case.module_feature}: {case.test_scenario}",
        "",
        f"**Severity:** {case.severity}",
        "",
    ]
    if case.preconditions:
        lines += ["## Preconditions", "", *(f"- {item}" for item in case.preconditions), ""]
    lines += ["## Test Steps", "", "| Step | Action | Expected Result |", "| --- | --- | --- |"]
    lines += [
        f"| {index} | {escape_cell(step.action)} | {escape_cell(step.expected_result)} |"
        for index, step in enumerate(case.steps, start=1)
    ]
    lines.append("")
    if case.notes:
        lines += ["## Notes", "", case.notes, ""]
    return "\n".join(lines).rstrip() + "\n"


def assign_ids(existing_names: list[str], count: int) -> list[str]:
    """The next `count` free `test-case-%04d` ids, after scanning `existing_names`."""
    numbers = [int(match.group(1)) for name in existing_names if (match := _ID.search(name))]
    start = max(numbers, default=0) + 1
    return [f"test-case-{start + index:04d}" for index in range(count)]


@dataclass(frozen=True)
class CaseWriter:
    """Writes cases into a directory of `test-case-<id>.md` files."""

    directory: Path
    base_url: str

    def write(self, cases: list[Case]) -> list[str]:
        """Render each case into `directory`, assigning the next free ids; return the file names."""
        self.directory.mkdir(parents=True, exist_ok=True)
        existing = [path.name for path in self.directory.glob("test-case-*.md")]
        names = [f"{id}.md" for id in assign_ids(existing, len(cases))]
        for name, case in zip(names, cases, strict=True):
            content = render_case(case, id=name.removesuffix(".md"), base_url=self.base_url)
            (self.directory / name).write_text(content, encoding="utf-8")
        return names
