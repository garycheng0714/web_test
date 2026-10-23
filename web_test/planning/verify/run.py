from collections.abc import Callable
from dataclasses import dataclass

from web_test.planning.review.jev import SystemOne, typesafe_system_one
from web_test.planning.review.parser import parse_test_case
from web_test.planning.review.report import render_report
from web_test.planning.review.service import run_review_on
from web_test.planning.review.verification import VerificationStatus
from web_test.planning.verify.cache import VerdictCache
from web_test.planning.verify.input import Approval, PreparedVerification
from web_test.planning.verify.key import InvalidTestCase, cache_key as compute_cache_key
from web_test.planning.verify.payload import (
    adjudicated_payload,
    approval_ignored_payload,
    early_payload,
    verdict_payload,
)
from web_test.planning.verify.resolution import ResolutionKind
from web_test.publishing.github import CheckPayload


@dataclass(frozen=True)
class RunResult:
    """The published check and whether its verdict was written to the cache."""

    payload: CheckPayload
    saved: bool
    status: VerificationStatus | None = None
    overridden: bool = False


@dataclass(frozen=True)
class _Adjudication:
    payload: CheckPayload
    overridden: bool


def _adjudicate(
    payload: CheckPayload,
    status: VerificationStatus,
    *,
    approval: Approval | None,
    head_sha: str,
) -> _Adjudication:
    if approval is None or not approval.applies_to(head_sha):
        return _Adjudication(payload=payload, overridden=False)
    if status in (VerificationStatus.NEEDS_REVIEW, VerificationStatus.BLOCKED):
        return _Adjudication(
            payload=adjudicated_payload(
                payload,
                original=status,
                reason=approval.reason,
                head_sha=head_sha,
            ),
            overridden=True,
        )
    if status is VerificationStatus.FAIL:
        return _Adjudication(
            payload=approval_ignored_payload(
                payload,
                original=status,
                reason=approval.reason,
                head_sha=head_sha,
            ),
            overridden=False,
        )
    return _Adjudication(payload=payload, overridden=False)


def run(
    prepared_verification: PreparedVerification,
    *,
    head_sha: str,
    publish: Callable[[CheckPayload], None],
    name: str = "verify-test-case",
    system_one: SystemOne = typesafe_system_one,
    cache: VerdictCache | None = None,
    approval: Approval | None = None,
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

    saved = False
    cached = cache.load(stored_key) if cache is not None else None
    if cached is not None:
        status = cached.status
        payload = cached.payload.model_copy(update={"head_sha": head_sha, "name": name})
    else:
        subject = parse_test_case(test_case_text, prd_text)
        record = run_review_on(subject, test_case_text, system_one=system_one)
        status = record.result.status
        payload = verdict_payload(
            status,
            summary=render_report(record),
            head_sha=head_sha,
            name=name,
            external_id=stored_key,
        )
        if cache is not None and status is not VerificationStatus.BLOCKED:
            cache.save(status, payload)
            saved = True

    adjudication = _adjudicate(
        payload,
        status,
        approval=approval,
        head_sha=head_sha,
    )
    publish(adjudication.payload)
    return RunResult(
        payload=adjudication.payload,
        saved=saved,
        status=status,
        overridden=adjudication.overridden,
    )
