from web_test.planning.review import Verdict
from web_test.planning.schema import DesignOutput

REVIEW_THRESHOLD = 0.8


def _label(question_id: str, design: DesignOutput) -> str:
    index = int(question_id.split("_")[1])
    return f"Case {index}: {design.cases[index - 1].test_scenario}"


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
    grounded_ok = sum(
        1
        for i in range(1, cases + 1)
        if (verdict := decisions.get(f"grounded_{i}")) is not None and verdict.value is True
    )

    findings = [
        f"{_label(qid, design)} (p={verdict.probability})"
        for qid, verdict in decisions.items()
        if verdict.value is False
    ]
    low = [
        f"{_label(qid, design)} (confidence={round(confidence, 2)})"
        for qid, verdict in decisions.items()
        if (confidence := _confidence(verdict)) is not None and confidence < threshold
    ]

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
