from dataclasses import replace

from web_test.planning.review import JevAnswer, run_review
from web_test.planning.review.report import render_report
from web_test.planning.schema import Case, DesignOutput
from web_test.planning.review.verification import (
    DeterministicOutcome,
    Override,
    VerificationStatus,
    digest_text,
)



def _case(**overrides):
    data = {
        "requirement_ids": ["FR-ACC-01"],
        "module_feature": "Account",
        "test_scenario": "Register",
        "steps": [{"action": "Go", "expected_result": "Page shown"}],
        "priority": "High",
        "severity": "Critical",
        "test_type": "Functional",
        **overrides,
    }
    return Case.model_validate(data)


def _design():
    return DesignOutput(
        cases=[_case(test_scenario="A"), _case(test_scenario="B"), _case(test_scenario="C")]
    )


def _answers(request, **overrides):
    values = {question_id: JevAnswer(0.95) for question_id in request.questions}
    values.update(overrides)
    return values


def _record(**overrides):
    return run_review(
        "# PRD",
        _design(),
        "artifact",
        system_one=lambda request: _answers(request, **overrides),
    )


def test_render_report_shows_status_counts_findings_and_evidence():
    record = _record(ac_2=JevAnswer(0.05), step_3_1_continuity=JevAnswer(0.6))

    text = render_report(record)

    assert "**Status:** `FAIL`" in text
    assert "**AC alignment:** 2/3 cases aligned" in text
    assert "**Step quality:** 3/3 reasonable, 2/3 continuity, 3/3 observable" in text
    assert "Case 2: B (AC alignment, p=0.05)" in text
    assert "Case 3, step 1: Go (continuity, p=0.6)" in text
    assert f"PRD: `sha256:{digest_text('# PRD')}`" in text
    assert f"Test Case: `sha256:{digest_text('artifact')}`" in text
    assert "Model: `jev-1.13.0`" in text
    assert "Question set: `" in text


def test_render_report_shows_blocked_reason():
    record = run_review(
        "# PRD",
        _design(),
        "artifact",
        system_one=lambda request: (_ for _ in ()).throw(RuntimeError("no key")),
    )

    text = render_report(record)

    assert "**Status:** `BLOCKED`" in text
    assert "Jev call failed: no key" in text
    assert f"Test Case: `sha256:{digest_text('artifact')}`" in text


def test_render_report_shows_a_reason_when_every_check_is_blocked():
    record = run_review(
        "# PRD",
        _design(),
        "artifact",
        system_one=lambda request: {"surprise": JevAnswer(0.95)},
    )

    text = render_report(record)

    assert "**Status:** `BLOCKED`" in text
    assert "No answer was returned for any check." in text


def test_render_report_shows_none_when_clean():
    text = render_report(_record())

    assert "**Status:** `PASS`" in text
    assert "**Findings**\n\nNone." in text
    assert "**Needs review**\n\nNone." in text
    assert "**Blocked**\n\nNone." in text


def test_render_report_ignores_unknown_question_ids():
    record = _record(surprise=JevAnswer(0.01))

    text = render_report(record)

    assert "surprise" not in text
    assert "**AC alignment:** 3/3 cases aligned" in text


def test_render_report_records_an_override():
    record = _record(step_3_1_continuity=JevAnswer(0.6))
    adjudicated = replace(
        record,
        result=replace(
            record.result,
            status=VerificationStatus.PASS,
            override=Override(
                original=VerificationStatus.NEEDS_REVIEW,
                reason="Expected result is observable in the PRD.",
                head_sha="abc123",
            ),
        ),
    )

    text = render_report(adjudicated)

    assert "**Status:** `PASS`" in text
    assert "NEEDS_REVIEW -> PASS at abc123" in text
    assert "Expected result is observable in the PRD." in text


def test_render_report_shows_the_structure_section():
    record = _record()
    structured = replace(
        record,
        result=replace(
            record.result,
            status=VerificationStatus.FAIL,
            jev_status=VerificationStatus.PASS,
            structure=(
                DeterministicOutcome(
                    "front_matter",
                    "Front matter is present and valid",
                    VerificationStatus.FAIL,
                    "front matter is missing or invalid",
                ),
            ),
        ),
    )

    text = render_report(structured)

    assert "**Status:** `FAIL`" in text
    assert "## Structure" in text
    assert "**Structure status:** `FAIL`; 0/1 checks passed" in text
    assert "**Jev status:** `PASS`" in text
    assert "front matter is missing or invalid" in text
    assert "Check set: `structure-v1`" in text
