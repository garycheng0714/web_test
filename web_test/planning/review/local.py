from pathlib import Path

from web_test.planning.review.jev import SystemOne, _typesafe_system_one
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.record import DEFAULT_BANDS
from web_test.planning.review.service import run_review_on
from web_test.planning.review.verification import Bands, VerificationRecord


def review_case_file(
    case_path: str | Path,
    prd_path: str | Path,
    *,
    system_one: SystemOne = _typesafe_system_one,
    bands: Bands = DEFAULT_BANDS,
) -> VerificationRecord:
    """Review the current contents of an existing Test Case file."""
    artifact_text = Path(case_path).read_text(encoding="utf-8")
    prd_text = Path(prd_path).read_text(encoding="utf-8")
    subject = parse_test_case(artifact_text, prd_text)
    return run_review_on(subject, artifact_text, system_one=system_one, bands=bands)
