from web_test.planning.review import Verdict
from web_test.planning.schema import DesignOutput

REVIEW_THRESHOLD = 0.8
_LABEL_LIMIT = 120
_STEP_CHECKS = ("reasonable", "complete", "observable")


def _text(value: str) -> str:
    text = " ".join(value.split())
    return text if len(text) <= _LABEL_LIMIT else f"{text[:_LABEL_LIMIT - 1]}…"


def _case_label(index: int, design: DesignOutput) -> str:
    return f"Case {index}: {_text(design.cases[index - 1].test_scenario)}"


def _step_label(case_index: int, step_index: int, design: DesignOutput) -> str:
    action = design.cases[case_index - 1].steps[step_index - 1].action
    return f"Case {case_index}, step {step_index}: {_text(action)}"


def _confidence(verdict: Verdict) -> float | None:
    """How sure Jev is of the answer *it gave*: a `noul` reports P(yes), so invert when it said no."""
    if verdict.probability is None:
        return None
    if verdict.value is False:
        return 1 - verdict.probability
    return float(verdict.probability)


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "None."


def _record(
    verdict: Verdict,
    label: str,
    check: str,
    findings: list[str],
    low: list[str],
    threshold: float,
) -> None:
    if verdict.value is False:
        findings.append(f"{label} ({check}, p={verdict.probability})")
    if (confidence := _confidence(verdict)) is not None and confidence < threshold:
        low.append(f"{label} ({check}, confidence={round(confidence, 2)})")


def render_report(
    decisions: dict[str, Verdict], design: DesignOutput, *, threshold: float = REVIEW_THRESHOLD
) -> str:
    """A compact advisory report: the three checks, their findings, and low-confidence items."""
    cases = len(design.cases)
    steps = [
        (case_index, step_index)
        for case_index, case in enumerate(design.cases, start=1)
        for step_index, _ in enumerate(case.steps, start=1)
    ]
    aligned, findings, low = 0, [], []

    for index in range(1, cases + 1):
        if (verdict := decisions.get(f"ac_{index}")) is None:
            continue
        if verdict.value is True:
            aligned += 1
        _record(verdict, _case_label(index, design), "AC alignment", findings, low, threshold)

    counts = {check: 0 for check in _STEP_CHECKS}
    for case_index, step_index in steps:
        for check in _STEP_CHECKS:
            verdict = decisions.get(f"step_{case_index}_{step_index}_{check}")
            if verdict is None:
                continue
            if verdict.value is True:
                counts[check] += 1
            _record(
                verdict,
                _step_label(case_index, step_index, design),
                check,
                findings,
                low,
                threshold,
            )

    step_total = len(steps)
    return "\n".join(
        [
            "## Jev review (advisory)",
            "",
            f"**AC alignment:** {aligned}/{cases} cases aligned",
            "",
            f"**Step quality:** {counts['reasonable']}/{step_total} reasonable, "
            f"{counts['complete']}/{step_total} complete, "
            f"{counts['observable']}/{step_total} observable",
            "",
            "**Findings**",
            "",
            _bullets(findings),
            "",
            f"**Needs review (confidence < {threshold})**",
            "",
            _bullets(low),
            "",
            "_Advisory: Jev does not block; a human decides._",
        ]
    )
