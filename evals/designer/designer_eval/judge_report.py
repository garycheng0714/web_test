"""Render one judge run's metrics as the markdown report."""

from evals.designer.designer_eval.judge_records import JudgeMetrics


def format_rate(value: float | None, interval: tuple[float, float] | None) -> str:
    if value is None or interval is None:
        return "n/a"
    return f"{value:.2f} [{interval[0]:.2f}, {interval[1]:.2f}]"


def render_report(metrics: JudgeMetrics, groups: dict[str, JudgeMetrics] | None = None) -> str:
    lines = [
        "# Designer judge report",
        "",
        f"- Claims: {metrics.total}",
        f"- Human labels: {metrics.human_fail} fail, {metrics.human_pass} pass",
        f"- Judge verdicts: {metrics.judged_fail} fail, {metrics.judged_pass} pass",
        "",
        "## Metrics",
        "",
        "| Metric | Definition | Value (Wilson 95% CI) |",
        "| --- | --- | --- |",
        (
            f"| Fail recall | judge fails when the human fails | "
            f"{format_rate(metrics.fail_recall, metrics.fail_recall_ci)} |"
        ),
        (
            f"| Pass specificity | judge passes when the human passes | "
            f"{format_rate(metrics.pass_specificity, metrics.pass_specificity_ci)} |"
        ),
        "",
        "## Confusion",
        "",
        "| | human fail | human pass |",
        "| --- | --- | --- |",
        f"| judge fail | {metrics.caught} | {metrics.false_alarm} |",
        f"| judge pass | {metrics.missed} | {metrics.agreed_pass} |",
        "",
    ]
    if groups and len(groups) > 1:
        lines += [
            "## By source run",
            "",
            "| source run | claims | fail recall | pass specificity |",
            "| --- | --- | --- | --- |",
        ]
        for source, group in groups.items():
            lines.append(
                f"| `{source}` | {group.total} | "
                f"{format_rate(group.fail_recall, group.fail_recall_ci)} | "
                f"{format_rate(group.pass_specificity, group.pass_specificity_ci)} |"
            )
        lines.append("")
    lines += ["## Disagreements", ""]
    if not metrics.disagreements:
        lines.append("None.")
    for record in metrics.disagreements:
        lines.append(
            f"- `{record.claim_id}` ({record.source_run}): human `{record.human_label}`"
            + (f" / {record.human_mode}" if record.human_mode else "")
            + f", judge `{record.verdict}` - {record.critique.strip().splitlines()[0][:160]}"
        )
    lines += [
        "",
        "## Limits",
        "",
        "- Dev only: every dataset holds one PRD, so these rates cannot be a held-out estimate.",
        "- A rate is `n/a` when the human labels contain no example of that class.",
        "- Legacy multi-requirement cases are excluded unless `--include-multi-fr` is passed.",
    ]
    return "\n".join(lines) + "\n"
