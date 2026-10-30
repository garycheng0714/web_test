from collections.abc import Sequence

from web_test.planning.review.verification import VerificationStatus
from web_test.planning.verify.resolution import ResolutionKind
from web_test.publishing.github import CheckConclusion, CheckPayload

_CONCLUSIONS: dict[VerificationStatus, CheckConclusion] = {
    VerificationStatus.PASS: "success",
    VerificationStatus.NEEDS_REVIEW: "action_required",
    VerificationStatus.FAIL: "failure",
    VerificationStatus.BLOCKED: "failure",
}


def early_payload(
    kind: ResolutionKind,
    *,
    head_sha: str,
    name: str,
    files: Sequence[str] = (),
    detail: str = "",
) -> CheckPayload:
    """Build the check payload for a resolution that never reaches Jev."""
    if kind is ResolutionKind.NOTHING:
        return CheckPayload(
            name=name,
            head_sha=head_sha,
            conclusion="success",
            title="Test Case verification: no Test Case file",
            summary="This PR does not change a `test-case/test-case-*.md` file.",
            external_id="no-test-case",
        )
    if kind is ResolutionKind.MULTIPLE:
        listed = "\n".join(f"- `{path}`" for path in files)
        return CheckPayload(
            name=name,
            head_sha=head_sha,
            conclusion="failure",
            title="Test Case verification: multiple Test Case files",
            summary=f"Exactly one Test Case file is supported per PR.\n\n{listed}",
            external_id="multiple-test-cases",
        )
    if kind is ResolutionKind.MISSING_PRD:
        return CheckPayload(
            name=name,
            head_sha=head_sha,
            conclusion="failure",
            title="Test Case verification: missing PRD",
            summary=f"The PRD was not found: `{detail}`",
            external_id="missing-prd",
        )
    if kind is ResolutionKind.INVALID:
        return CheckPayload(
            name=name,
            head_sha=head_sha,
            conclusion="failure",
            title="Test Case verification: invalid Test Case",
            summary=detail or "The Test Case file could not be read.",
            external_id="invalid-test-case",
        )
    raise ValueError("a ready verification input needs a review")


def verdict_payload(
    status: VerificationStatus,
    *,
    summary: str,
    head_sha: str,
    name: str,
    external_id: str,
) -> CheckPayload:
    """Build the check payload for a Jev verdict."""
    return CheckPayload(
        name=name,
        head_sha=head_sha,
        conclusion=_CONCLUSIONS[status],
        title=f"Test Case verification: {status.value}",
        summary=summary,
        external_id=external_id,
    )


def _reason(reason: str) -> str:
    return "\n".join(f"> {line}" for line in reason.splitlines())


def _with_adjudication(
    payload: CheckPayload,
    *,
    original: VerificationStatus,
    reason: str,
    head_sha: str,
    overridden: bool,
) -> CheckPayload:
    if overridden:
        outcome = "- This override applies to this head only; a new head needs a fresh verdict."
    else:
        outcome = (
            "- Approval ignored: `FAIL` is not overridable; fix the Test Case or the question set."
        )
    section = "\n".join(
        (
            "",
            "## Human adjudication",
            "",
            f"- Original verdict: `{original.value}`",
            f"- Head: `{head_sha}`",
            outcome,
            "",
            "**Reason:**",
            "",
            _reason(reason),
        )
    )
    title = "Test Case verification: PASS (adjudicated)" if overridden else payload.title
    return payload.model_copy(
        update={
            "conclusion": "success" if overridden else payload.conclusion,
            "title": title,
            "summary": payload.summary + section,
        }
    )


def adjudicated_payload(
    payload: CheckPayload,
    *,
    original: VerificationStatus,
    reason: str,
    head_sha: str,
) -> CheckPayload:
    """Turn a NEEDS_REVIEW or BLOCKED payload into an adjudicated success."""
    return _with_adjudication(
        payload,
        original=original,
        reason=reason,
        head_sha=head_sha,
        overridden=True,
    )


def approval_ignored_payload(
    payload: CheckPayload,
    *,
    original: VerificationStatus,
    reason: str,
    head_sha: str,
) -> CheckPayload:
    """Keep a FAIL verdict, recording that an approval did not apply."""
    return _with_adjudication(
        payload,
        original=original,
        reason=reason,
        head_sha=head_sha,
        overridden=False,
    )
