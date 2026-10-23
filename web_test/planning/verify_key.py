import yaml

from web_test.planning.review.jev import JEV_MODEL
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.questions import (
    question_set_version,
    questions_for_subject,
)
from web_test.planning.review.record import DEFAULT_BANDS
from web_test.planning.review.verification import digest_text


class InvalidTestCase(ValueError):
    """The Test Case could not be parsed for a verdict key."""


def cache_key(test_case_text: str, prd_text: str) -> str:
    """Hash the Test Case, PRD, question set, model, and bands into the verdict key."""
    try:
        subject = parse_test_case(test_case_text, prd_text)
    except (ValueError, yaml.YAMLError) as error:
        raise InvalidTestCase(str(error)) from error
    version = question_set_version(questions_for_subject(subject))
    return _cache_key(
        digest_text(test_case_text),
        digest_text(prd_text),
        version,
    )


def _cache_key(test_case_digest: str, prd_digest: str, version: str) -> str:
    payload = "\n".join(
        [
            test_case_digest,
            prd_digest,
            version,
            JEV_MODEL,
            str(DEFAULT_BANDS.pass_min),
            str(DEFAULT_BANDS.needs_review_min),
        ]
    )
    return digest_text(payload)
