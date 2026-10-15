from web_test.planning.review import Verdict
from web_test.planning.schema import DesignOutput

REVIEW_THRESHOLD = 0.8


def _label(index: int, design: DesignOutput) -> str:
    scenario = " ".join(design.cases[index - 1].test_scenario.split())
    return f"Case {index}: {scenario}"


def _confidence(verdict: Verdict) -> float | None:
    """How sure Jev is of the answer *it gave*: a `noul` reports P(yes), so invert when it said no."""
    if verdict.probability is None:
        return None
    if verdict.value is False:
        return 1 - verdict.probability
    return float(verdict.probability)


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "None."


def render_report(
    decisions: dict[str, Verdict], design: DesignOutput, *, threshold: float = REVIEW_THRESHOLD
) -> str:
    """A compact advisory report: the groundedness summary, the findings, and low-confidence items."""
    cases = len(design.cases)
    grounded_ok, findings, low = 0, [], []

    # Walk the known ids (`grounded_1..N`); any other key Jev returns is ignored, so rendering
    # never raises on an unexpected answer.
    for index in range(1, cases + 1):
        if (verdict := decisions.get(f"grounded_{index}")) is None:
            continue
        if verdict.value is True:
            grounded_ok += 1
        elif verdict.value is False:
            findings.append(f"{_label(index, design)} (p={verdict.probability})")
        if (confidence := _confidence(verdict)) is not None and confidence < threshold:
            low.append(f"{_label(index, design)} (confidence={round(confidence, 2)})")

    return "\n".join(
        [
            "## Jev review (advisory)",
            "",
            f"**Groundedness:** {grounded_ok}/{cases} grounded",
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
