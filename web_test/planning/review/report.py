from web_test.planning.review.questions import STEP_QUALITY_DIMENSIONS
from web_test.planning.review.verification import (
    CheckDimension,
    CheckOutcome,
    VerificationRecord,
    VerificationStatus,
    worst,
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
    result = record.result
    binding = record.binding
    checks = result.checks
    cases = len(result.cases)
    steps = len(result.steps)

    findings = [_item(check) for check in checks if check.status is VerificationStatus.FAIL]
    needs_review = [
        _item(check) for check in checks if check.status is VerificationStatus.NEEDS_REVIEW
    ]
    blocked_checks = [_item(check) for check in checks if check.status is VerificationStatus.BLOCKED]
    blocked = []
    if result.blocked_reason:
        blocked.append(result.blocked_reason)
    if blocked_checks and len(blocked_checks) != len(checks):
        blocked.extend(blocked_checks)

    lines = [
        "## Verification",
        "",
        f"**Status:** `{result.status.value}`",
    ]

    if result.structure:
        structure_status = worst(outcome.status for outcome in result.structure)
        passed = sum(
            1
            for outcome in result.structure
            if outcome.status is VerificationStatus.PASS
        )
        failures = [
            f"- {_text(outcome.label)}: {_text(outcome.detail)}"
            for outcome in result.structure
            if outcome.status is VerificationStatus.FAIL
        ]
        lines += [
            "",
            "## Structure",
            "",
            f"**Structure status:** `{structure_status.value}`; "
            f"{passed}/{len(result.structure)} checks passed",
            "",
            "**Structure findings**",
            "",
            _bullets(failures),
        ]

    lines += [
        "",
        "## Jev review",
        "",
        f"**Jev status:** `{(result.jev_status or result.status).value}`",
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

    if result.override:
        target = result.override.head_sha or "current head"
        lines += [
            "",
            "**Override**",
            "",
            f"- {result.override.original.value} -> {result.status.value} at {target}: "
            f"{result.override.reason}",
        ]

    lines += [
        "",
        "**Evidence**",
        "",
        f"- PRD: `sha256:{binding.prd_digest}`",
        f"- Test Case: `sha256:{binding.test_case_digest}`",
        f"- Model: `{binding.model}`",
        f"- Question set: `{binding.question_set_version}`",
        f"- Check set: `{binding.check_set_version}`",
        f"- Bands: pass >= {binding.bands.pass_min}, "
        f"needs review >= {binding.bands.needs_review_min}",
        "",
        "_Required-check contract: PASS or an adjudicated NEEDS_REVIEW/BLOCKED; FAIL is not overridable._",
    ]
    return "\n".join(lines)
