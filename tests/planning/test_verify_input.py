import pytest

from web_test.planning.verify.input import Approval, PreparedVerification
from web_test.planning.verify.resolution import ResolutionKind


def test_ready_input_requires_all_verdict_fields() -> None:
    with pytest.raises(ValueError, match="missing its verdict data"):
        PreparedVerification(kind=ResolutionKind.READY)


def test_early_input_rejects_verdict_fields() -> None:
    with pytest.raises(ValueError, match="has verdict data"):
        PreparedVerification(
            kind=ResolutionKind.NOTHING,
            test_case_text="case",
            prd_text="prd",
            cache_key="key",
        )


def test_approval_trims_the_reason_and_head() -> None:
    approval = Approval.model_validate(
        {"state": "approved", "reason": "  looks good  ", "head_sha": " sha "}
    )

    assert approval.reason == "looks good"
    assert approval.head_sha == "sha"
    assert approval.applies_to("sha") is True


def test_approval_does_not_apply_to_another_head() -> None:
    approval = Approval(state="approved", reason="looks good", head_sha="sha")

    assert approval.applies_to("other") is False


def test_approval_does_not_apply_without_a_reason() -> None:
    approval = Approval(state="approved", reason="   ", head_sha="sha")

    assert approval.reason == ""
    assert approval.applies_to("sha") is False


def test_approval_does_not_apply_without_an_approved_state() -> None:
    approval = Approval(state="commented", reason="looks good", head_sha="sha")

    assert approval.applies_to("sha") is False


def test_approval_limits_the_reason() -> None:
    approval = Approval(state="approved", reason="x" * 5000, head_sha="sha")

    assert len(approval.reason) == 4000
    assert approval.reason.endswith("…")


def test_approval_does_not_apply_without_a_head() -> None:
    approval = Approval(state="approved", reason="looks good", head_sha="  ")

    assert approval.applies_to("") is False
