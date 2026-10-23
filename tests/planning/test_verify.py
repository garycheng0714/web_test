from pathlib import Path

import pytest

from web_test.planning.cases_writer import render_document
from web_test.planning.review.jev import JevAnswer
from web_test.planning.schema import Case
from web_test.planning.verify import cli
from web_test.planning.verify.cache import VerdictCache
from web_test.planning.verify.input import PreparedVerification
from web_test.planning.verify.prepare import prepare
from web_test.planning.verify.resolution import ResolutionKind
from web_test.planning.verify.run import RunResult, run
from web_test.publishing.github import CheckPayload, GitHubError


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


def _run_payload(*args, **kwargs):
    return run(*args, **kwargs).payload


def _ready_input(tmp_path: Path) -> PreparedVerification:
    case_path, _ = _write_case(tmp_path)
    _write_prd(tmp_path)
    return prepare([case_path], workspace=tmp_path)


def test_prepare_builds_a_ready_input(tmp_path: Path) -> None:
    case_path, case_text = _write_case(tmp_path)
    _write_prd(tmp_path)

    verification_input = prepare([case_path], workspace=tmp_path)

    assert verification_input.kind is ResolutionKind.READY
    assert verification_input.cache_key is not None
    assert len(verification_input.cache_key) == 64
    assert verification_input.test_case_text == case_text
    assert verification_input.prd_text == "# PRD"


def test_prepare_builds_an_early_input(tmp_path: Path) -> None:
    verification_input = prepare([], workspace=tmp_path)

    assert verification_input.kind is ResolutionKind.NOTHING
    assert verification_input.test_case_text is None


def test_prepare_marks_a_test_case_without_cases_invalid(tmp_path: Path) -> None:
    path = tmp_path / "test-case" / "test-case-demo.md"
    path.parent.mkdir()
    path.write_text("---\nid: demo\n---\n\n# Demo\n", encoding="utf-8")
    _write_prd(tmp_path)

    verification_input = prepare(["test-case/test-case-demo.md"], workspace=tmp_path)

    assert verification_input.kind is ResolutionKind.INVALID
    assert "no '## Case N' sections" in verification_input.detail


def test_run_rejects_a_ready_input_without_verdict_data() -> None:
    _, publish = _sink()

    with pytest.raises(ValueError, match="missing its verdict data"):
        run(
            PreparedVerification(kind=ResolutionKind.READY),
            head_sha="sha",
            publish=publish,
            system_one=_never_called,
        )


def test_run_publishes_success_when_nothing_changed() -> None:
    payloads, publish = _sink()

    payload = _run_payload(
        PreparedVerification(kind=ResolutionKind.NOTHING),
        head_sha="sha",
        publish=publish,
        system_one=_never_called,
    )

    assert payload.conclusion == "success"
    assert "no Test Case file" in payload.title
    assert payload.external_id == "no-test-case"
    assert payloads == [payload]


def test_run_publishes_failure_for_multiple_files() -> None:
    verification_input = PreparedVerification(
        kind=ResolutionKind.MULTIPLE,
        files=["test-case/test-case-a.md", "test-case/test-case-b.md"],
    )
    payloads, publish = _sink()

    payload = _run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=_never_called
    )

    assert payload.conclusion == "failure"
    assert "multiple" in payload.title
    assert "test-case-a.md" in payload.summary
    assert payloads == [payload]


def test_run_publishes_failure_for_a_missing_prd() -> None:
    verification_input = PreparedVerification(kind=ResolutionKind.MISSING_PRD, detail="/repo/prd/demo.md")
    payloads, publish = _sink()

    payload = _run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=_never_called
    )

    assert payload.conclusion == "failure"
    assert "missing PRD" in payload.title
    assert "/repo/prd/demo.md" in payload.summary


def test_run_publishes_failure_for_an_invalid_artifact() -> None:
    verification_input = PreparedVerification(kind=ResolutionKind.INVALID, detail="no '## Case N' sections")
    payloads, publish = _sink()

    payload = _run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=_never_called
    )

    assert payload.conclusion == "failure"
    assert "invalid" in payload.title
    assert "no '## Case N' sections" in payload.summary


def test_run_publishes_pass(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)
    payloads, publish = _sink()

    payload = _run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=_passing_system_one
    )

    assert payload.conclusion == "success"
    assert payload.title == "Test Case verification: PASS"
    assert "## Jev review" in payload.summary
    assert verification_input.cache_key is not None
    assert payload.external_id == verification_input.cache_key
    assert payloads == [payload]


def test_run_publishes_needs_review(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)
    payloads, publish = _sink()

    payload = _run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=_one_answer(0.6)
    )

    assert payload.conclusion == "action_required"
    assert payload.title == "Test Case verification: NEEDS_REVIEW"


def test_run_publishes_fail(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)
    payloads, publish = _sink()

    payload = _run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=_one_answer(0.1)
    )

    assert payload.conclusion == "failure"
    assert payload.title == "Test Case verification: FAIL"


def test_run_publishes_blocked_when_jev_returns_nothing(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)
    payloads, publish = _sink()

    payload = _run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=_empty_system_one
    )

    assert payload.conclusion == "failure"
    assert payload.title == "Test Case verification: BLOCKED"
    assert "Blocked" in payload.summary


def test_run_propagates_publish_errors(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)

    def publish(payload):
        raise GitHubError("boom")

    with pytest.raises(GitHubError, match="boom"):
        run(verification_input, head_sha="sha", publish=publish, system_one=_passing_system_one)


def test_run_uses_a_cached_verdict(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)
    assert verification_input.cache_key is not None
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text(
        CheckPayload(
            head_sha="old",
            conclusion="success",
            title="Test Case verification: PASS",
            summary="cached summary",
            external_id=verification_input.cache_key,
        ).model_dump_json(),
        encoding="utf-8",
    )
    payloads, publish = _sink()

    result = run(
        verification_input,
        head_sha="new",
        publish=publish,
        system_one=_never_called,
        cache=cache,
    )
    payload = result.payload

    assert payload.summary == "cached summary"
    assert payload.head_sha == "new"
    assert payload.external_id == verification_input.cache_key
    assert result.saved is False
    assert payloads == [payload]


def test_run_saves_a_new_verdict(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)
    assert verification_input.cache_key is not None
    cache = VerdictCache(tmp_path / "cache")
    _, publish = _sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=_passing_system_one,
        cache=cache,
    )
    payload = result.payload

    assert result.saved is True
    assert cache.load(verification_input.cache_key) == payload
    assert payload.external_id == verification_input.cache_key


def test_run_does_not_cache_blocked(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)
    cache = VerdictCache(tmp_path / "cache")
    _, publish = _sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=_empty_system_one,
        cache=cache,
    )
    payload = result.payload

    assert payload.title == "Test Case verification: BLOCKED"
    assert result.saved is False
    assert not cache.path.exists()


def test_run_ignores_a_cache_for_another_key(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text(
        CheckPayload(
            head_sha="old",
            conclusion="failure",
            title="Test Case verification: FAIL",
            summary="stale",
            external_id="another-key",
        ).model_dump_json(),
        encoding="utf-8",
    )
    _, publish = _sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=_passing_system_one,
        cache=cache,
    )
    payload = result.payload

    assert payload.title == "Test Case verification: PASS"
    assert result.saved is True


def test_run_ignores_a_corrupt_cache(tmp_path: Path) -> None:
    verification_input = _ready_input(tmp_path)
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text("{not json", encoding="utf-8")
    _, publish = _sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=_passing_system_one,
        cache=cache,
    )
    payload = result.payload

    assert payload.title == "Test Case verification: PASS"
    assert result.saved is True


def test_cli_run_reports_a_cache_hit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    verification_input = _ready_input(tmp_path)
    assert verification_input.cache_key is not None
    input_path = tmp_path / "verification-input.json"
    input_path.write_text(verification_input.model_dump_json(), encoding="utf-8")
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "verdict.json").write_text(
        CheckPayload(
            head_sha="old",
            conclusion="success",
            title="Test Case verification: PASS",
            summary="cached summary",
            external_id=verification_input.cache_key,
        ).model_dump_json(),
        encoding="utf-8",
    )
    output = tmp_path / "github-output.txt"
    published = []

    class FakeAdapter:
        def publish_check(self, payload):
            published.append(payload)

        @classmethod
        def from_env(cls):
            return cls()

    real_run = cli.run

    def guarded_run(verification_input, *, head_sha, publish, name, cache):
        return real_run(
            verification_input,
            head_sha=head_sha,
            publish=publish,
            name=name,
            cache=cache,
            system_one=_never_called,
        )

    monkeypatch.setattr(cli, "run", guarded_run)
    monkeypatch.setattr(cli, "GitHubAdapter", FakeAdapter)

    result = cli.main(
        [
            "run",
            "--verification-input",
            str(input_path),
            "--head-sha",
            "sha",
            "--cache-dir",
            str(cache_dir),
            "--github-output",
            str(output),
        ]
    )

    assert result == 0
    assert published[0].summary == "cached summary"
    assert published[0].head_sha == "sha"
    assert output.read_text(encoding="utf-8") == "saved=false\n"


def test_cli_run_reports_a_saved_verdict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    verification_input = _ready_input(tmp_path)
    input_path = tmp_path / "verification-input.json"
    input_path.write_text(verification_input.model_dump_json(), encoding="utf-8")
    output = tmp_path / "github-output.txt"
    published = []

    def fake_run(verification_input, *, head_sha, publish, name, cache):
        assert verification_input.cache_key is not None
        payload = CheckPayload(
            head_sha=head_sha,
            conclusion="success",
            title="Test Case verification: PASS",
            summary="new summary",
            external_id=verification_input.cache_key,
        )
        cache.save(payload)
        publish(payload)
        return RunResult(payload=payload, saved=True)

    class FakeAdapter:
        def publish_check(self, payload):
            published.append(payload)

        @classmethod
        def from_env(cls):
            return cls()

    monkeypatch.setattr(cli, "run", fake_run)
    monkeypatch.setattr(cli, "GitHubAdapter", FakeAdapter)

    result = cli.main(
        [
            "run",
            "--verification-input",
            str(input_path),
            "--head-sha",
            "sha",
            "--cache-dir",
            str(tmp_path / "cache"),
            "--github-output",
            str(output),
        ]
    )

    assert result == 0
    assert published[0].summary == "new summary"
    assert output.read_text(encoding="utf-8") == "saved=true\n"


def test_cli_prepare_writes_the_cache_key(tmp_path: Path) -> None:
    case_path, case_text = _write_case(tmp_path)
    _write_prd(tmp_path)
    changed = tmp_path / "changed.txt"
    changed.write_text(f"{case_path}\n", encoding="utf-8")
    input_path = tmp_path / "verification-input.json"
    output = tmp_path / "github-output.txt"

    result = cli.main(
        [
            "prepare",
            "--changed-files",
            str(changed),
            "--workspace",
            str(tmp_path),
            "--verification-input",
            str(input_path),
            "--github-output",
            str(output),
        ]
    )

    assert result == 0
    key = output.read_text(encoding="utf-8").strip().removeprefix("key=")
    assert len(key) == 64
    written = PreparedVerification.model_validate_json(
        input_path.read_text(encoding="utf-8")
    )
    assert written.cache_key == key
    assert written.test_case_text == case_text
    assert written.prd_text == "# PRD"


def test_cli_run_publishes_an_early_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path = tmp_path / "verification-input.json"
    input_path.write_text(
        PreparedVerification(kind=ResolutionKind.NOTHING).model_dump_json(), encoding="utf-8"
    )
    published = []

    class FakeAdapter:
        def publish_check(self, payload):
            published.append(payload)

        @classmethod
        def from_env(cls):
            return cls()

    monkeypatch.setattr(cli, "GitHubAdapter", FakeAdapter)

    result = cli.main(
        ["run", "--verification-input", str(input_path), "--head-sha", "sha"]
    )

    assert result == 0
    assert published[0].conclusion == "success"


def test_cli_run_returns_one_when_publishing_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    input_path = tmp_path / "verification-input.json"
    input_path.write_text(
        PreparedVerification(kind=ResolutionKind.NOTHING).model_dump_json(), encoding="utf-8"
    )

    class FakeAdapter:
        def publish_check(self, payload):
            raise GitHubError("boom")

        @classmethod
        def from_env(cls):
            return cls()

    monkeypatch.setattr(cli, "GitHubAdapter", FakeAdapter)

    result = cli.main(
        ["run", "--verification-input", str(input_path), "--head-sha", "sha"]
    )

    assert result == 1
    assert "failed: boom" in capsys.readouterr().err


def test_cli_run_fails_fast_without_github_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    input_path = tmp_path / "verification-input.json"
    input_path.write_text(
        PreparedVerification(kind=ResolutionKind.NOTHING).model_dump_json(), encoding="utf-8"
    )
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    result = cli.main(["run", "--verification-input", str(input_path), "--head-sha", "sha"])

    assert result == 1
    assert "failed:" in capsys.readouterr().err
