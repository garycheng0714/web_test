from pathlib import Path

import pytest

from web_test.planning.verify.input import PreparedVerification
from web_test.planning.verify.resolution import ResolutionKind
from web_test.planning.verify.run import run
from web_test.publishing.github import GitHubError
from verify_helpers import (
    empty_system_one,
    never_called,
    one_answer,
    passing_system_one,
    ready_input,
    run_payload,
    sink,
)


def test_run_rejects_a_ready_input_without_verdict_data() -> None:
    _, publish = sink()

    with pytest.raises(ValueError, match="missing its verdict data"):
        run(
            PreparedVerification.model_construct(kind=ResolutionKind.READY),
            head_sha="sha",
            publish=publish,
            system_one=never_called,
        )


def test_run_rejects_a_mismatched_cache_key(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    tampered = verification_input.model_copy(update={"cache_key": "0" * 64})
    _, publish = sink()

    with pytest.raises(ValueError, match="cache key"):
        run(
            tampered,
            head_sha="sha",
            publish=publish,
            system_one=never_called,
        )


def test_run_publishes_success_when_nothing_changed() -> None:
    payloads, publish = sink()

    payload = run_payload(
        PreparedVerification(kind=ResolutionKind.NOTHING),
        head_sha="sha",
        publish=publish,
        system_one=never_called,
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
    payloads, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=never_called
    )

    assert payload.conclusion == "failure"
    assert "multiple" in payload.title
    assert "test-case-a.md" in payload.summary
    assert payloads == [payload]

def test_run_publishes_failure_for_a_missing_prd() -> None:
    verification_input = PreparedVerification(kind=ResolutionKind.MISSING_PRD, detail="/repo/prd/demo.md")
    payloads, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=never_called
    )

    assert payload.conclusion == "failure"
    assert "missing PRD" in payload.title
    assert "/repo/prd/demo.md" in payload.summary

def test_run_publishes_failure_for_an_invalid_artifact() -> None:
    verification_input = PreparedVerification(kind=ResolutionKind.INVALID, detail="no '## Case N' sections")
    payloads, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=never_called
    )

    assert payload.conclusion == "failure"
    assert "invalid" in payload.title
    assert "no '## Case N' sections" in payload.summary

def test_run_publishes_pass(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    payloads, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=passing_system_one
    )

    assert payload.conclusion == "success"
    assert payload.title == "Test Case verification: PASS"
    assert "## Jev review" in payload.summary
    assert verification_input.cache_key is not None
    assert payload.external_id == verification_input.cache_key
    assert payloads == [payload]

def test_run_publishes_needs_review(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    payloads, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=one_answer(0.6)
    )

    assert payload.conclusion == "action_required"
    assert payload.title == "Test Case verification: NEEDS_REVIEW"

def test_run_publishes_fail(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    payloads, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=one_answer(0.1)
    )

    assert payload.conclusion == "failure"
    assert payload.title == "Test Case verification: FAIL"

def test_run_publishes_blocked_when_jev_returns_nothing(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    payloads, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=empty_system_one
    )

    assert payload.conclusion == "failure"
    assert payload.title == "Test Case verification: BLOCKED"
    assert "Blocked" in payload.summary

def test_run_propagates_publish_errors(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)

    def publish(payload):
        raise GitHubError("boom")

    with pytest.raises(GitHubError, match="boom"):
        run(verification_input, head_sha="sha", publish=publish, system_one=passing_system_one)
