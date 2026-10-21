import re

import yaml

from web_test.planning.review.subject import ReviewCase, ReviewStep, ReviewSubject

_CASE_HEADING = re.compile(r"(?m)^## Case (\d+): (.*)$")
_YAML_BLOCK = re.compile(r"```yaml\n(.*?)\n```", re.S)
_CELL_SEPARATOR = re.compile(r"(?<!\\)\|")


def _metadata(section: str) -> dict[str, object]:
    match = _YAML_BLOCK.search(section)
    if match is None:
        return {}
    data = yaml.safe_load(match.group(1)) or {}
    return data if isinstance(data, dict) else {}


def _requirement_ids(section: str) -> list[str]:
    raw = _metadata(section).get("requirement_ids", [])
    if isinstance(raw, str):
        return [raw]
    return [str(item) for item in raw] if isinstance(raw, list) else []


def _cells(line: str) -> list[str]:
    return [
        cell.strip().replace(r"\|", "|")
        for cell in _CELL_SEPARATOR.split(line.strip().strip("|"))
    ]


def _preconditions(section: str) -> list[str]:
    lines = section.splitlines()
    try:
        start = lines.index("### Preconditions")
    except ValueError:
        return []

    items = []
    for line in lines[start + 1 :]:
        if line.startswith("## ") or line.startswith("### "):
            break
        if line.strip().startswith("- "):
            items.append(line.strip()[2:].strip())
    return items


def _steps(section: str) -> list[ReviewStep]:
    lines = section.splitlines()
    try:
        start = lines.index("### Test Steps")
    except ValueError:
        return []

    steps = []
    for line in lines[start + 1 :]:
        if line.startswith("## ") or line.startswith("### "):
            break
        if not line.strip().startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) < 3 or cells[0].lower() == "step" or set(cells[0]) <= {"-", ":"}:
            continue
        steps.append(
            ReviewStep(index=int(cells[0]), action=cells[1], expected_result=cells[2])
        )
    return steps


def _case_parts(heading: str) -> tuple[str, str]:
    # shortcut: generated headings use ": " as the separator; a colon inside module_feature
    # is ambiguous. Upgrade if headings need an escaped separator.
    module_feature, separator, test_scenario = heading.partition(": ")
    return (module_feature, test_scenario) if separator else ("", heading)


def parse_test_case(text: str, prd_text: str) -> ReviewSubject:
    """Read a rendered Test Case file back into the review subject it was built from."""
    matches = list(_CASE_HEADING.finditer(text))
    if not matches:
        raise ValueError("no '## Case N' sections found")

    cases = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end() : end]
        module_feature, test_scenario = _case_parts(match.group(2).strip())
        cases.append(
            ReviewCase(
                index=int(match.group(1)),
                requirement_ids=_requirement_ids(section),
                module_feature=module_feature,
                test_scenario=test_scenario,
                preconditions=_preconditions(section),
                steps=_steps(section),
            )
        )
    return ReviewSubject(prd=prd_text, cases=cases)
