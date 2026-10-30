from pathlib import Path

import pytest

from verify_helpers import (
    approval,
    empty_system_one,
    never_called,
    one_answer,
    passing_system_one,
    ready_input,
    run_payload,
    sink,
)
from web_test.planning.review.verification import VerificationStatus
from web_test.planning.verify.cache import CachedVerdict, VerdictCache
from web_test.planning.verify.input import PreparedVerification
from web_test.planning.verify.resolution import ResolutionKind
from web_test.planning.verify.run import run
from web_test.publishing.github import CheckPayload, GitHubError


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
    verification_input = PreparedVerification(
        kind=ResolutionKind.MISSING_PRD, detail="/repo/prd/demo.md"
    )
    _, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=never_called
    )

    assert payload.conclusion == "failure"
    assert "missing PRD" in payload.title
    assert "/repo/prd/demo.md" in payload.summary


def test_run_publishes_failure_for_an_invalid_artifact() -> None:
    verification_input = PreparedVerification(
        kind=ResolutionKind.INVALID, detail="no '## Case N' sections"
    )
    _, publish = sink()

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
    _, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=one_answer(0.6)
    )

    assert payload.conclusion == "action_required"
    assert payload.title == "Test Case verification: NEEDS_REVIEW"


def test_run_publishes_fail(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    _, publish = sink()

    payload = run_payload(
        verification_input, head_sha="sha", publish=publish, system_one=one_answer(0.1)
    )

    assert payload.conclusion == "failure"
    assert payload.title == "Test Case verification: FAIL"


def test_run_publishes_blocked_when_jev_returns_nothing(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    _, publish = sink()

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


def test_run_applies_an_approval_to_needs_review(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    payloads, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=one_answer(0.6),
        approval=approval(reason="accepted the wording"),
    )

    assert result.status is VerificationStatus.NEEDS_REVIEW
    assert result.overridden is True
    assert result.payload.conclusion == "success"
    assert result.payload.title == "Test Case verification: PASS (adjudicated)"
    assert "Original verdict: `NEEDS_REVIEW`" in result.payload.summary
    assert "accepted the wording" in result.payload.summary
    assert "`sha`" in result.payload.summary
    assert payloads == [result.payload]


def test_run_applies_an_approval_to_blocked(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=empty_system_one,
        approval=approval(reason="Jev was unavailable"),
    )

    assert result.status is VerificationStatus.BLOCKED
    assert result.saved is False
    assert result.overridden is True
    assert result.payload.conclusion == "success"
    assert "Original verdict: `BLOCKED`" in result.payload.summary


def test_run_keeps_fail_when_approved(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    payloads, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=one_answer(0.1),
        approval=approval(reason="looks fine to me"),
    )

    assert result.status is VerificationStatus.FAIL
    assert result.overridden is False
    assert result.payload.conclusion == "failure"
    assert result.payload.title == "Test Case verification: FAIL"
    assert "Approval ignored" in result.payload.summary
    assert "looks fine to me" in result.payload.summary
    assert payloads == [result.payload]


def test_run_ignores_an_approval_on_a_different_head(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=one_answer(0.6),
        approval=approval(head_sha="other"),
    )

    assert result.status is VerificationStatus.NEEDS_REVIEW
    assert result.overridden is False
    assert result.payload.conclusion == "action_required"
    assert "Human adjudication" not in result.payload.summary


def test_run_ignores_an_approval_without_a_reason(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=one_answer(0.6),
        approval=approval(reason="   "),
    )

    assert result.status is VerificationStatus.NEEDS_REVIEW
    assert result.overridden is False
    assert result.payload.conclusion == "action_required"


def test_run_ignores_a_non_approved_review(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=one_answer(0.6),
        approval=approval(state="commented"),
    )

    assert result.status is VerificationStatus.NEEDS_REVIEW
    assert result.overridden is False
    assert result.payload.conclusion == "action_required"


def test_run_does_not_override_an_early_outcome() -> None:
    verification_input = PreparedVerification(
        kind=ResolutionKind.MULTIPLE,
        files=["test-case/test-case-a.md", "test-case/test-case-b.md"],
    )
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=never_called,
        approval=approval(),
    )

    assert result.status is None
    assert result.overridden is False
    assert result.payload.conclusion == "failure"
    assert "Human adjudication" not in result.payload.summary


def test_run_leaves_pass_unchanged_with_an_approval(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    _, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=passing_system_one,
        approval=approval(),
    )

    assert result.status is VerificationStatus.PASS
    assert result.overridden is False
    assert result.payload.conclusion == "success"
    assert result.payload.title == "Test Case verification: PASS"
    assert "Human adjudication" not in result.payload.summary


def test_run_uses_a_cached_verdict_with_an_approval(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path)
    assert verification_input.cache_key is not None
    cache = VerdictCache(tmp_path / "cache")
    cache.directory.mkdir()
    cache.path.write_text(
        CachedVerdict(
            status=VerificationStatus.NEEDS_REVIEW,
            payload=CheckPayload(
                head_sha="old",
                conclusion="action_required",
                title="Test Case verification: NEEDS_REVIEW",
                summary="cached summary",
                external_id=verification_input.cache_key,
            ),
        ).model_dump_json(),
        encoding="utf-8",
    )
    payloads, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=never_called,
        cache=cache,
        approval=approval(reason="accepted after review"),
    )

    assert result.overridden is True
    assert result.payload.conclusion == "success"
    assert "cached summary" in result.payload.summary
    assert "Original verdict: `NEEDS_REVIEW`" in result.payload.summary
    assert payloads == [result.payload]


def test_run_fails_on_a_structure_error_and_ignores_an_approval(tmp_path: Path) -> None:
    verification_input = ready_input(tmp_path, steps=[{"action": "Go", "expected_result": ""}])
    payloads, publish = sink()

    result = run(
        verification_input,
        head_sha="sha",
        publish=publish,
        system_one=passing_system_one,
        approval=approval(reason="looks fine"),
    )

    assert result.status is VerificationStatus.FAIL
    assert result.overridden is False
    assert result.payload.conclusion == "failure"
    assert result.payload.title == "Test Case verification: FAIL"
    assert "## Structure" in result.payload.summary
    assert "expected result is empty" in result.payload.summary
    assert "Approval ignored" in result.payload.summary
    assert "Original verdict: `FAIL`" in result.payload.summary
    assert payloads == [result.payload]
