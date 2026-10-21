from web_test.planning.review.questions import STEP_QUALITY_DIMENSIONS
from web_test.planning.review.verification import (
    CheckDimension,
    CheckOutcome,
    VerificationStatus,
    VerificationRecord,
)

_LABEL_LIMIT = 120


def _text(value: str) -> str:
    text = " ".join(value.split())
    return text if len(text) <= _LABEL_LIMIT else f"{text[:_LABEL_LIMIT - 1]}…"


def _probability(value: float | None) -> str:
    return "n/a" if value is None else str(round(value, 2))


def _item(check: CheckOutcome) -> str:
    return f"{_text(check.label)} ({check.dimension}, p={_probability(check.probability)})"


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "None."


def _count(checks: tuple[CheckOutcome, ...], dimension: CheckDimension) -> int:
    return sum(
        1
        for check in checks
        if check.dimension == dimension and check.status is VerificationStatus.PASS
    )


def render_report(record: VerificationRecord) -> str:
    """Render the verification record as the PR body section and the check summary."""
    checks = record.checks
    cases = len(record.cases)
    steps = len(record.steps)

    findings = [_item(check) for check in checks if check.status is VerificationStatus.FAIL]
    needs_review = [
        _item(check) for check in checks if check.status is VerificationStatus.NEEDS_REVIEW
    ]
    blocked_checks = [_item(check) for check in checks if check.status is VerificationStatus.BLOCKED]
    blocked = []
    if record.blocked_reason:
        blocked.append(record.blocked_reason)
    if blocked_checks and len(blocked_checks) != len(checks):
        blocked.extend(blocked_checks)

    lines = [
        "## Jev review",
        "",
        f"**Status:** `{record.status.value}`",
        "",
        f"**AC alignment:** {_count(checks, CheckDimension.AC_ALIGNMENT)}/{cases} cases aligned",
        "",
        "**Step quality:** "
        + ", ".join(
            f"{_count(checks, dimension)}/{steps} {dimension}"
            for dimension in STEP_QUALITY_DIMENSIONS
        ),
        "",
        "**Findings**",
        "",
        _bullets(findings),
        "",
        "**Needs review**",
        "",
        _bullets(needs_review),
        "",
        "**Blocked**",
        "",
        _bullets(blocked),
    ]

    if record.override:
        target = record.override.head_sha or "current head"
        lines += [
            "",
            "**Override**",
            "",
            f"- {record.override.original.value} -> {record.status.value} at {target}: "
            f"{record.override.reason}",
        ]

    lines += [
        "",
        "**Evidence**",
        "",
        f"- PRD: `sha256:{record.prd_digest}`",
        f"- Artifact: `sha256:{record.artifact_digest}`",
        f"- Model: `{record.model}`",
        f"- Question set: `{record.question_set_version}`",
        f"- Bands: pass >= {record.bands.pass_min}, "
        f"needs review >= {record.bands.needs_review_min}",
        "",
        "_Required-check contract: PASS or an adjudicated NEEDS_REVIEW/BLOCKED; FAIL is not overridable._",
    ]
    return "\n".join(lines)
