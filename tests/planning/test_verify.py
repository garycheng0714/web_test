from pathlib import Path

import pytest

from web_test.planning import verify
from web_test.planning.cases_writer import render_document
from web_test.planning.review.jev import JevAnswer
from web_test.planning.review.verification import digest_text
from web_test.planning.schema import Case
from web_test.planning.verify import Plan, ResolutionKind, prepare, resolve, run
from web_test.publishing.github import GitHubError


def _case() -> Case:
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


def _write_case(
    root: Path, case_id: str = "demo", *, title: str = "Demo"
) -> tuple[str, str]:
    text = render_document(
        [_case()], id=case_id, base_url="https://example.com", title=title
    )
    path = root / "test-case" / f"test-case-{case_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return f"test-case/test-case-{case_id}.md", text


def _write_prd(root: Path, case_id: str = "demo", text: str = "# PRD") -> Path:
    path = root / "prd" / f"{case_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_nothing_when_no_artifact_changed(tmp_path: Path) -> None:
    (tmp_path / "test-case").mkdir()
    (tmp_path / "test-case" / "notes.md").write_text("notes", encoding="utf-8")

    assert resolve([], workspace=tmp_path).kind is ResolutionKind.NOTHING
    assert (
        resolve(["test-case/notes.md", "prd/demo.md"], workspace=tmp_path).kind
        is ResolutionKind.NOTHING
    )


def test_ready_binds_the_digests_and_the_key(tmp_path: Path) -> None:
    case_path, case_text = _write_case(tmp_path)
    prd_path = _write_prd(tmp_path)

    result = resolve([case_path], workspace=tmp_path)

    assert result.kind is ResolutionKind.READY
    check = result.check_input
    assert check is not None
    assert check.case_path == Path(case_path)
    assert check.prd_path == prd_path
    assert check.test_case_digest == digest_text(case_text)
    assert check.prd_digest == digest_text("# PRD")
    assert check.question_set_version
    assert len(check.cache_key) == 64


def test_multiple_artifacts_are_reported(tmp_path: Path) -> None:
    first, _ = _write_case(tmp_path, "one")
    second, _ = _write_case(tmp_path, "two")

    result = resolve([second, first], workspace=tmp_path)

    assert result.kind is ResolutionKind.MULTIPLE
    assert result.files == (first, second)
    assert result.check_input is None


def test_missing_prd_is_reported(tmp_path: Path) -> None:
    case_path, _ = _write_case(tmp_path)

    result = resolve([case_path], workspace=tmp_path)

    assert result.kind is ResolutionKind.MISSING_PRD
    assert str(tmp_path / "prd" / "demo.md") in result.detail


def test_unreadable_prd_is_invalid(tmp_path: Path, monkeypatch) -> None:
    case_path, _ = _write_case(tmp_path)
    prd_path = _write_prd(tmp_path)
    original_read_text = Path.read_text

    def read_text(self: Path, *args, **kwargs):
        if self == prd_path:
            raise PermissionError("denied")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)

    result = resolve([case_path], workspace=tmp_path)

    assert result.kind is ResolutionKind.INVALID
    assert "reading PRD" in result.detail
    assert str(prd_path) in result.detail


def test_an_artifact_without_cases_is_invalid(tmp_path: Path) -> None:
    path = tmp_path / "test-case" / "test-case-demo.md"
    path.parent.mkdir()
    path.write_text("---\nid: demo\n---\n\n# Demo\n", encoding="utf-8")
    _write_prd(tmp_path)

    result = resolve(["test-case/test-case-demo.md"], workspace=tmp_path)

    assert result.kind is ResolutionKind.INVALID
    assert "no '## Case N' sections" in result.detail


def test_missing_front_matter_is_invalid(tmp_path: Path) -> None:
    path = tmp_path / "test-case" / "test-case-demo.md"
    path.parent.mkdir()
    path.write_text("# Demo\n", encoding="utf-8")
    _write_prd(tmp_path)

    result = resolve(["test-case/test-case-demo.md"], workspace=tmp_path)

    assert result.kind is ResolutionKind.INVALID
    assert "missing front matter" in result.detail


def test_a_missing_front_matter_id_is_invalid(tmp_path: Path) -> None:
    path = tmp_path / "test-case" / "test-case-demo.md"
    path.parent.mkdir()
    path.write_text("---\nbase_url: https://example.com\n---\n", encoding="utf-8")
    _write_prd(tmp_path)

    result = resolve(["test-case/test-case-demo.md"], workspace=tmp_path)

    assert result.kind is ResolutionKind.INVALID
    assert "string id" in result.detail


def test_cache_key_is_stable_and_sensitive(tmp_path: Path) -> None:
    case_path, case_text = _write_case(tmp_path)
    _write_prd(tmp_path)

    first = resolve([case_path], workspace=tmp_path).check_input
    second = resolve([case_path], workspace=tmp_path).check_input
    assert first is not None and second is not None
    assert first.cache_key == second.cache_key

    (tmp_path / case_path).write_text(case_text + "\n", encoding="utf-8")
    changed_case = resolve([case_path], workspace=tmp_path).check_input
    assert changed_case is not None
    assert changed_case.cache_key != first.cache_key

    _write_prd(tmp_path, text="# PRD v2")
    changed_prd = resolve([case_path], workspace=tmp_path).check_input
    assert changed_prd is not None
    assert changed_prd.cache_key != changed_case.cache_key


def test_cache_key_includes_the_question_set_version(
    tmp_path: Path, monkeypatch
) -> None:
    case_path, _ = _write_case(tmp_path)
    _write_prd(tmp_path)
    monkeypatch.setattr(
        "web_test.planning.verify.question_set_version",
        lambda questions: "v1",
    )
    first = resolve([case_path], workspace=tmp_path).check_input

    monkeypatch.setattr(
        "web_test.planning.verify.question_set_version",
        lambda questions: "v2",
    )
    second = resolve([case_path], workspace=tmp_path).check_input

    assert first is not None and second is not None
    assert first.question_set_version == "v1"
    assert second.question_set_version == "v2"
    assert first.cache_key != second.cache_key


def _passing_system_one(request):
    return {question_id: JevAnswer(0.95) for question_id in request.questions}


def _one_answer(first: float, rest: float = 0.95):
    def system_one(request):
        values = {question_id: JevAnswer(rest) for question_id in request.questions}
        values[next(iter(request.questions))] = JevAnswer(first)
        return values

    return system_one


def _empty_system_one(request):
    return {}


def _never_called(request):
    raise AssertionError("Jev must not be called")


def _sink():
    payloads = []

    def publish(payload):
        payloads.append(payload)

    return payloads, publish


def _ready_plan(tmp_path: Path) -> Plan:
    case_path, _ = _write_case(tmp_path)
    _write_prd(tmp_path)
    return prepare(
        [case_path], workspace=tmp_path, plan_path=tmp_path / "plan.json"
    )


def test_prepare_writes_a_ready_plan(tmp_path: Path) -> None:
    case_path, _ = _write_case(tmp_path)
    prd_path = _write_prd(tmp_path)
    plan_path = tmp_path / "plan.json"

    plan = prepare([case_path], workspace=tmp_path, plan_path=plan_path)

    assert plan.kind is ResolutionKind.READY
    assert plan.check_input is not None
    assert len(plan.check_input.cache_key) == 64
    reloaded = Plan.model_validate_json(plan_path.read_text(encoding="utf-8"))
    assert reloaded == plan
    assert reloaded.check_input is not None
    assert reloaded.check_input.case_path == Path(case_path)
    assert reloaded.check_input.prd_path == prd_path


def test_prepare_writes_an_early_plan(tmp_path: Path) -> None:
    plan = prepare([], workspace=tmp_path, plan_path=tmp_path / "plan.json")

    assert plan.kind is ResolutionKind.NOTHING
    assert plan.check_input is None


def test_run_publishes_success_when_nothing_changed() -> None:
    payloads, publish = _sink()

    payload = run(
        Plan(kind=ResolutionKind.NOTHING),
        head_sha="sha",
        publish=publish,
        system_one=_never_called,
    )

    assert payload.conclusion == "success"
    assert "no Test Case file" in payload.title
    assert payload.external_id == "no-test-case"
    assert payloads == [payload]


def test_run_publishes_failure_for_multiple_files() -> None:
    plan = Plan(
        kind=ResolutionKind.MULTIPLE,
        files=["test-case/test-case-a.md", "test-case/test-case-b.md"],
    )
    payloads, publish = _sink()

    payload = run(
        plan, head_sha="sha", publish=publish, system_one=_never_called
    )

    assert payload.conclusion == "failure"
    assert "multiple" in payload.title
    assert "test-case-a.md" in payload.summary
    assert payloads == [payload]


def test_run_publishes_failure_for_a_missing_prd() -> None:
    plan = Plan(kind=ResolutionKind.MISSING_PRD, detail="/repo/prd/demo.md")
    payloads, publish = _sink()

    payload = run(
        plan, head_sha="sha", publish=publish, system_one=_never_called
    )

    assert payload.conclusion == "failure"
    assert "missing PRD" in payload.title
    assert "/repo/prd/demo.md" in payload.summary


def test_run_publishes_failure_for_an_invalid_artifact() -> None:
    plan = Plan(kind=ResolutionKind.INVALID, detail="no '## Case N' sections")
    payloads, publish = _sink()

    payload = run(
        plan, head_sha="sha", publish=publish, system_one=_never_called
    )

    assert payload.conclusion == "failure"
    assert "invalid" in payload.title
    assert "no '## Case N' sections" in payload.summary


def test_run_publishes_pass(tmp_path: Path) -> None:
    plan = _ready_plan(tmp_path)
    payloads, publish = _sink()

    payload = run(
        plan, head_sha="sha", publish=publish, system_one=_passing_system_one
    )

    assert payload.conclusion == "success"
    assert payload.title == "Test Case verification: PASS"
    assert "## Jev review" in payload.summary
    assert plan.check_input is not None
    assert payload.external_id == plan.check_input.cache_key
    assert payloads == [payload]


def test_run_publishes_needs_review(tmp_path: Path) -> None:
    plan = _ready_plan(tmp_path)
    payloads, publish = _sink()

    payload = run(
        plan, head_sha="sha", publish=publish, system_one=_one_answer(0.6)
    )

    assert payload.conclusion == "action_required"
    assert payload.title == "Test Case verification: NEEDS_REVIEW"


def test_run_publishes_fail(tmp_path: Path) -> None:
    plan = _ready_plan(tmp_path)
    payloads, publish = _sink()

    payload = run(
        plan, head_sha="sha", publish=publish, system_one=_one_answer(0.1)
    )

    assert payload.conclusion == "failure"
    assert payload.title == "Test Case verification: FAIL"


def test_run_publishes_blocked_when_jev_returns_nothing(tmp_path: Path) -> None:
    plan = _ready_plan(tmp_path)
    payloads, publish = _sink()

    payload = run(
        plan, head_sha="sha", publish=publish, system_one=_empty_system_one
    )

    assert payload.conclusion == "failure"
    assert payload.title == "Test Case verification: BLOCKED"
    assert "Blocked" in payload.summary


def test_run_propagates_publish_errors(tmp_path: Path) -> None:
    plan = _ready_plan(tmp_path)

    def publish(payload):
        raise GitHubError("boom")

    with pytest.raises(GitHubError, match="boom"):
        run(plan, head_sha="sha", publish=publish, system_one=_passing_system_one)


def test_cli_prepare_writes_the_cache_key(tmp_path: Path) -> None:
    case_path, _ = _write_case(tmp_path)
    _write_prd(tmp_path)
    changed = tmp_path / "changed.txt"
    changed.write_text(f"{case_path}\n", encoding="utf-8")
    output = tmp_path / "github-output.txt"

    result = verify.main(
        [
            "prepare",
            "--changed-files",
            str(changed),
            "--workspace",
            str(tmp_path),
            "--plan",
            str(tmp_path / "plan.json"),
            "--github-output",
            str(output),
        ]
    )

    assert result == 0
    key = output.read_text(encoding="utf-8").strip().removeprefix("key=")
    assert len(key) == 64


def test_cli_run_publishes_an_early_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        Plan(kind=ResolutionKind.NOTHING).model_dump_json(), encoding="utf-8"
    )
    published = []

    class FakeAdapter:
        def publish_check(self, payload):
            published.append(payload)

        @classmethod
        def from_env(cls):
            return cls()

    monkeypatch.setattr(verify, "GitHubAdapter", FakeAdapter)

    result = verify.main(
        ["run", "--plan", str(plan_path), "--head-sha", "sha"]
    )

    assert result == 0
    assert published[0].conclusion == "success"


def test_cli_run_returns_one_when_publishing_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        Plan(kind=ResolutionKind.NOTHING).model_dump_json(), encoding="utf-8"
    )

    class FakeAdapter:
        def publish_check(self, payload):
            raise GitHubError("boom")

        @classmethod
        def from_env(cls):
            return cls()

    monkeypatch.setattr(verify, "GitHubAdapter", FakeAdapter)

    result = verify.main(
        ["run", "--plan", str(plan_path), "--head-sha", "sha"]
    )

    assert result == 1
    assert "failed: boom" in capsys.readouterr().err
