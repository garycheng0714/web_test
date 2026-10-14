from web_test.planning.schema import Case


def _cell(value: str) -> str:
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
        f"| {index} | {_cell(step.action)} | {_cell(step.expected_result)} |"
        for index, step in enumerate(case.steps, start=1)
    ]
    lines.append("")
    if case.notes:
        lines += ["## Notes", "", case.notes, ""]
    return "\n".join(lines).rstrip() + "\n"
