import yaml

from web_test.planning.review.jev import JEV_MODEL
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.questions import (
    question_set_version,
    questions_for_subject,
)
from web_test.planning.review.record import DEFAULT_BANDS
from web_test.planning.review.structure import CHECK_SET_VERSION
from web_test.planning.review.verification import digest_text


class InvalidTestCase(ValueError):
    """The Test Case could not be parsed for a verdict key."""


def cache_key(
    test_case_text: str,
    prd_text: str,
    *,
    check_set_version: str = CHECK_SET_VERSION,
) -> str:
    """Hash the Test Case, PRD, Jev question set, model, bands, and structure rules into the key."""
    try:
        subject = parse_test_case(test_case_text, prd_text)
    except (ValueError, yaml.YAMLError) as error:
        raise InvalidTestCase(str(error)) from error
    version = question_set_version(questions_for_subject(subject))
    return _cache_key(
        digest_text(test_case_text),
        digest_text(prd_text),
        version,
        check_set_version,
    )


def _cache_key(test_case_digest: str, prd_digest: str, version: str, check_set_version: str) -> str:
    payload = "\n".join(
        [
            test_case_digest,
            prd_digest,
            version,
            JEV_MODEL,
            str(DEFAULT_BANDS.pass_min),
            str(DEFAULT_BANDS.needs_review_min),
            check_set_version,
        ]
    )
    return digest_text(payload)
