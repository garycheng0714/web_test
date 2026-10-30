from pathlib import Path

import pytest

from verify_helpers import never_called, ready_input, write_case, write_prd
from web_test.planning.review.verification import VerificationStatus
from web_test.planning.verify import cli
from web_test.planning.verify.cache import CachedVerdict
from web_test.planning.verify.input import Approval, PreparedVerification
from web_test.planning.verify.resolution import ResolutionKind
from web_test.planning.verify.run import RunResult
from web_test.publishing.github import CheckPayload, GitHubError


def test_cli_run_reports_a_cache_hit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    verification_input = ready_input(tmp_path)
    assert verification_input.cache_key is not None
    input_path = tmp_path / "verification-input.json"
    input_path.write_text(verification_input.model_dump_json(), encoding="utf-8")
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "verdict.json").write_text(
        CachedVerdict(
            status=VerificationStatus.PASS,
            payload=CheckPayload(
                head_sha="old",
                conclusion="success",
                title="Test Case verification: PASS",
                summary="cached summary",
                external_id=verification_input.cache_key,
            ),
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

    def guarded_run(
        verification_input, *, head_sha, publish, name, cache, approval=None
    ):
        return real_run(
            verification_input,
            head_sha=head_sha,
            publish=publish,
            name=name,
            cache=cache,
            system_one=never_called,
            approval=approval,
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
    verification_input = ready_input(tmp_path)
    input_path = tmp_path / "verification-input.json"
    input_path.write_text(verification_input.model_dump_json(), encoding="utf-8")
    output = tmp_path / "github-output.txt"
    published = []

    def fake_run(
        verification_input, *, head_sha, publish, name, cache, approval=None
    ):
        assert verification_input.cache_key is not None
        payload = CheckPayload(
            head_sha=head_sha,
            conclusion="success",
            title="Test Case verification: PASS",
            summary="new summary",
            external_id=verification_input.cache_key,
        )
        cache.save(VerificationStatus.PASS, payload)
        publish(payload)
        return RunResult(payload=payload, saved=True, status=VerificationStatus.PASS)

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
    case_path, case_text = write_case(tmp_path)
    write_prd(tmp_path)
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


def test_cli_run_passes_the_approval_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_path = tmp_path / "verification-input.json"
    input_path.write_text(
        PreparedVerification(kind=ResolutionKind.NOTHING).model_dump_json(),
        encoding="utf-8",
    )
    captured = {}

    class FakeAdapter:
        def publish_check(self, payload):
            captured["payload"] = payload

        @classmethod
        def from_env(cls):
            return cls()

    def fake_run(verification_input, *, head_sha, publish, name, cache, approval=None):
        captured["approval"] = approval
        payload = CheckPayload(
            head_sha=head_sha,
            conclusion="success",
            title="Test Case verification: no Test Case file",
            summary="no Test Case",
            external_id="no-test-case",
        )
        publish(payload)
        return RunResult(payload=payload, saved=False)

    monkeypatch.setattr(cli, "run", fake_run)
    monkeypatch.setattr(cli, "GitHubAdapter", FakeAdapter)

    result = cli.main(
        [
            "run",
            "--verification-input",
            str(input_path),
            "--head-sha",
            "sha",
            "--approval-state",
            "approved",
            "--approval-reason",
            "looks good",
            "--approval-head-sha",
            "sha",
        ]
    )

    assert result == 0
    assert captured["approval"] == Approval(
        state="approved", reason="looks good", head_sha="sha"
    )


def test_cli_run_rejects_partial_approval_flags(
    tmp_path: Path, capsys
) -> None:
    input_path = tmp_path / "verification-input.json"
    input_path.write_text(
        PreparedVerification(kind=ResolutionKind.NOTHING).model_dump_json(),
        encoding="utf-8",
    )

    result = cli.main(
        [
            "run",
            "--verification-input",
            str(input_path),
            "--head-sha",
            "sha",
            "--approval-state",
            "approved",
        ]
    )

    assert result == 1
    assert "approval flags must be provided together" in capsys.readouterr().err
