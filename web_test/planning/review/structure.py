import re
from collections import Counter

import yaml

from web_test.planning.review.subject import ReviewSubject
from web_test.planning.review.verification import (
    DeterministicOutcome,
    VerificationStatus,
)

# Bump when a deterministic rule changes; the cache key and the verdict evidence include it.
CHECK_SET_VERSION = "structure-v1"

_CASE_HEADING = re.compile(r"(?m)^## Case \d+: ")


def _outcome(
    check_id: str,
    label: str,
    *,
    passed: bool,
    detail: str = "",
) -> DeterministicOutcome:
    return DeterministicOutcome(
        check_id=check_id,
        label=label,
        status=VerificationStatus.PASS if passed else VerificationStatus.FAIL,
        detail=detail,
    )


def _front_matter(text: str) -> dict[str, object] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            break
    else:
        return None
    try:
        data = yaml.safe_load("\n".join(lines[1:index]))
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    return {str(key): value for key, value in data.items()}


def _front_matter_outcomes(text: str) -> tuple[DeterministicOutcome, ...]:
    data = _front_matter(text)
    if data is None:
        return (
            _outcome(
                "front_matter",
                "Front matter is present and valid",
                passed=False,
                detail="front matter is missing or invalid",
            ),
        )

    outcomes = []
    for key in ("id", "base_url"):
        value = data.get(key)
        passed = isinstance(value, str) and bool(value.strip())
        outcomes.append(
            _outcome(
                f"front_matter_{key}",
                f"Front matter: {key} is present",
                passed=passed,
                detail=f"{key} is missing or empty" if not passed else "",
            )
        )
    return tuple(outcomes)


def _case_number_outcomes(subject: ReviewSubject) -> tuple[DeterministicOutcome, ...]:
    numbers = [case.index for case in subject.cases]
    duplicates = sorted(number for number, count in Counter(numbers).items() if count > 1)
    if not duplicates:
        return (_outcome("case_numbers", "Case numbers are unique", passed=True),)
    listed = ", ".join(str(number) for number in duplicates)
    return (
        _outcome(
            "case_numbers",
            "Case numbers are unique",
            passed=False,
            detail=f"duplicate case numbers: {listed}",
        ),
    )


def _step_outcomes(subject: ReviewSubject) -> tuple[DeterministicOutcome, ...]:
    outcomes = []
    for case in subject.cases:
        outcomes.append(
            _outcome(
                f"case_{case.index}_steps",
                f"Case {case.index} has at least one step",
                passed=bool(case.steps),
                detail="case has no steps" if not case.steps else "",
            )
        )
        for step in case.steps:
            action = step.action.strip()
            expected = step.expected_result.strip()
            outcomes.append(
                _outcome(
                    f"step_{case.index}_{step.index}_action",
                    f"Case {case.index}, step {step.index}: action is non-empty",
                    passed=bool(action),
                    detail="action is empty" if not action else "",
                )
            )
            outcomes.append(
                _outcome(
                    f"step_{case.index}_{step.index}_expected",
                    f"Case {case.index}, step {step.index}: expected result is non-empty",
                    passed=bool(expected),
                    detail="expected result is empty" if not expected else "",
                )
            )
    return tuple(outcomes)


def structure_checks(
    subject: ReviewSubject, test_case_text: str
) -> tuple[DeterministicOutcome, ...]:
    """Run the deterministic structural checks for a rendered Test Case."""
    if not _CASE_HEADING.search(test_case_text):
        return ()
    return (
        *_front_matter_outcomes(test_case_text),
        *_case_number_outcomes(subject),
        *_step_outcomes(subject),
    )
