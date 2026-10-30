import pytest

from web_test.planning.review.verification import VerificationStatus
from web_test.planning.verify.payload import early_payload, verdict_payload
from web_test.planning.verify.resolution import ResolutionKind


def test_nothing_is_success() -> None:
    payload = early_payload(ResolutionKind.NOTHING, head_sha="sha", name="verify-test-case")

    assert payload.conclusion == "success"
    assert "no Test Case file" in payload.title
    assert payload.external_id == "no-test-case"
    assert payload.summary


def test_multiple_is_failure_with_the_files() -> None:
    payload = early_payload(
        ResolutionKind.MULTIPLE,
        head_sha="sha",
        name="verify-test-case",
        files=["test-case/test-case-a.md", "test-case/test-case-b.md"],
    )

    assert payload.conclusion == "failure"
    assert "multiple" in payload.title
    assert "test-case-a.md" in payload.summary
    assert "test-case-b.md" in payload.summary


def test_missing_prd_is_failure_with_the_detail() -> None:
    payload = early_payload(
        ResolutionKind.MISSING_PRD,
        head_sha="sha",
        name="verify-test-case",
        detail="/repo/prd/demo.md",
    )

    assert payload.conclusion == "failure"
    assert "missing PRD" in payload.title
    assert "/repo/prd/demo.md" in payload.summary


def test_invalid_is_failure_with_the_detail() -> None:
    payload = early_payload(
        ResolutionKind.INVALID,
        head_sha="sha",
        name="verify-test-case",
        detail="no '## Case N' sections",
    )

    assert payload.conclusion == "failure"
    assert "invalid" in payload.title
    assert "no '## Case N' sections" in payload.summary


def test_ready_is_not_an_early_payload() -> None:
    with pytest.raises(ValueError, match="ready verification input"):
        early_payload(ResolutionKind.READY, head_sha="sha", name="verify-test-case")


@pytest.mark.parametrize(
    ("status", "conclusion"),
    [
        (VerificationStatus.PASS, "success"),
        (VerificationStatus.NEEDS_REVIEW, "action_required"),
        (VerificationStatus.FAIL, "failure"),
        (VerificationStatus.BLOCKED, "failure"),
    ],
)
def test_verdict_payload_maps_the_status(status: VerificationStatus, conclusion: str) -> None:
    payload = verdict_payload(
        status,
        summary="summary",
        head_sha="sha",
        name="verify-test-case",
        external_id="key",
    )

    assert payload.conclusion == conclusion
    assert payload.title == f"Test Case verification: {status.value}"
    assert payload.summary == "summary"
    assert payload.external_id == "key"
    assert payload.head_sha == "sha"
    assert payload.name == "verify-test-case"
