from pathlib import Path

from web_test.planning.cases_writer import render_document
from web_test.planning.review.jev import JevAnswer
from web_test.planning.schema import Case
from web_test.planning.verify.input import PreparedVerification
from web_test.planning.verify.prepare import prepare
from web_test.planning.verify.run import run


def case() -> Case:
    return Case.model_validate(
        {
            "requirement_ids": ["FR-1"],
            "module_feature": "Account",
            "test_scenario": "Register",
            "steps": [{"action": "Go", "expected_result": "Page shown"}],
            "priority": "High",
            "severity": "Critical",
            "test_type": "Functional",
        }
    )


def case_text() -> str:
    return render_document(
        [case()], id="demo", base_url="https://example.com", title="Demo"
    )


def write_case(
    root: Path, case_id: str = "demo", *, title: str = "Demo"
) -> tuple[str, str]:
    text = render_document(
        [case()], id=case_id, base_url="https://example.com", title=title
    )
    path = root / "test-case" / f"test-case-{case_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return f"test-case/test-case-{case_id}.md", text


def write_prd(root: Path, case_id: str = "demo", text: str = "# PRD") -> Path:
    path = root / "prd" / f"{case_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def passing_system_one(request):
    return {question_id: JevAnswer(0.95) for question_id in request.questions}


def one_answer(first: float, rest: float = 0.95):
    def system_one(request):
        values = {question_id: JevAnswer(rest) for question_id in request.questions}
        values[next(iter(request.questions))] = JevAnswer(first)
        return values

    return system_one


def empty_system_one(request):
    return {}


def never_called(request):
    raise AssertionError("Jev must not be called")


def sink():
    payloads = []

    def publish(payload):
        payloads.append(payload)

    return payloads, publish


def run_payload(*args, **kwargs):
    return run(*args, **kwargs).payload


def ready_input(tmp_path: Path) -> PreparedVerification:
    case_path, _ = write_case(tmp_path)
    write_prd(tmp_path)
    return prepare([case_path], workspace=tmp_path)
