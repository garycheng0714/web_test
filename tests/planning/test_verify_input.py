import pytest

from web_test.planning.verify.input import PreparedVerification
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
