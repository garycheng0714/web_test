from pathlib import Path

from pydantic_ai.models import Model

from web_test.paths import PRD_PATH, TEST_CASES_PATH
from web_test.planning.designer import design_test_cases
from web_test.planning.document import write_report
from web_test.planning.schema import QaReport


def generate_test_cases(
    prd_path: str | Path = PRD_PATH,
    output_path: str | Path = TEST_CASES_PATH,
    *,
    model: Model | str | None = None,
    force: bool = False,
) -> QaReport:
    prd_text = Path(prd_path).read_text(encoding="utf-8")
    report = design_test_cases(prd_text, model=model)
    write_report(report, output_path, force=force)
    return report