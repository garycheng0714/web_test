from collections.abc import Callable
from dataclasses import dataclass

from web_test.planning.review.jev import SystemOne, typesafe_system_one
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.report import render_report
from web_test.planning.review.service import run_review_on
from web_test.planning.review.verification import VerificationStatus
from web_test.planning.verify.cache import VerdictCache
from web_test.planning.verify.input import PreparedVerification
from web_test.planning.verify.key import InvalidTestCase, cache_key as compute_cache_key
from web_test.planning.verify.payload import early_payload, verdict_payload
from web_test.planning.verify.resolution import ResolutionKind
from web_test.publishing.github import CheckPayload


@dataclass(frozen=True)
class RunResult:
    """The published check and whether its verdict was written to the cache."""

    payload: CheckPayload
    saved: bool


def run(
    prepared_verification: PreparedVerification,
    *,
    head_sha: str,
    publish: Callable[[CheckPayload], None],
    name: str = "verify-test-case",
    system_one: SystemOne = typesafe_system_one,
    cache: VerdictCache | None = None,
) -> RunResult:
    """Publish the check for the verification input: an early outcome, or the verdict."""
    if prepared_verification.kind is not ResolutionKind.READY:
        payload = early_payload(
            prepared_verification.kind,
            head_sha=head_sha,
            name=name,
            files=prepared_verification.files,
            detail=prepared_verification.detail,
        )
        publish(payload)
        return RunResult(payload=payload, saved=False)

    test_case_text = prepared_verification.test_case_text
    prd_text = prepared_verification.prd_text
    stored_key = prepared_verification.cache_key
    if test_case_text is None or prd_text is None or stored_key is None:
        raise ValueError("ready verification input is missing its verdict data")

    try:
        expected_key = compute_cache_key(test_case_text, prd_text)
    except InvalidTestCase as error:
        raise ValueError(f"verification input is invalid: {error}") from error
    if expected_key != stored_key:
        raise ValueError("verification input cache key does not match its texts")

    if cache is not None:
        cached = cache.load(stored_key)
        if cached is not None:
            payload = cached.model_copy(update={"head_sha": head_sha, "name": name})
            publish(payload)
            return RunResult(payload=payload, saved=False)

    subject = parse_test_case(test_case_text, prd_text)
    record = run_review_on(subject, test_case_text, system_one=system_one)
    payload = verdict_payload(
        record.result.status,
        summary=render_report(record),
        head_sha=head_sha,
        name=name,
        external_id=stored_key,
    )
    publish(payload)
    saved = False
    if cache is not None and record.result.status is not VerificationStatus.BLOCKED:
        cache.save(payload)
        saved = True
    return RunResult(payload=payload, saved=saved)
