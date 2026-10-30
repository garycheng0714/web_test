from pathlib import Path

from web_test.planning.review.eval import evaluate
from web_test.planning.review.eval_report import render_eval_report
from web_test.planning.review.eval_set import EvalSet, load_eval_set
from web_test.planning.review.jev import JevAnswer

_FIXTURES = (
    Path(__file__).parent.parent
    / "fixtures"
    / "review_eval"
    / "register_login_golden_v1.json"
)


def _eval_set(*, require_each_dimension: bool = False, expected_failures=None) -> EvalSet:
    return EvalSet.model_validate(
        {
            "prd": "# PRD",
            "cases": [
                {
                    "id": "G1",
                    "label": "good",
                    "requirement_ids": ["FR-1"],
                    "scenario": "Good case",
                    "steps": [
                        {"action": "Go", "expected_result": "Page shown"},
                    ],
                },
                {
                    "id": "B1",
                    "label": "bad",
                    "tests": "skipped required step",
                    "requirement_ids": ["FR-1"],
                    "scenario": "Bad continuity",
                    "steps": [
                        {"action": "Click Submit", "expected_result": "Done"},
                    ],
                },
                {
                    "id": "B2",
                    "label": "bad",
                    "tests": "contradicts the AC",
                    "requirement_ids": ["FR-1"],
                    "scenario": "Bad AC",
                    "steps": [
                        {"action": "Go", "expected_result": "Page shown"},
                    ],
                },
            ],
            "expected_failures": expected_failures
            or [
                {"case": "B1", "dimension": "continuity", "step": 1},
                {"case": "B2", "dimension": "AC alignment"},
            ],
            "kill_criteria": {
                "caught_min": 2,
                "hard_fail_min": 1,
                "good_false_flags_max": 0,
                "bad_blocked_max": 0,
                "require_each_dimension": require_each_dimension,
            },
        }
    )


def _system_one(overrides):
    def system_one(request):
        return {
            question_id: overrides.get(question_id, JevAnswer(0.95))
            for question_id in request.questions
        }

    return system_one


def test_evaluate_counts_catches_false_flags_and_hard_failures():
    report = evaluate(
        _eval_set(),
        system_one=_system_one(
            {
                "step_2_1_continuity": JevAnswer(0.1),
                "ac_3": JevAnswer(0.6),
            }
        ),
    )

    assert report.caught == 2
    assert report.expected == 2
    assert report.hard_fail == 1
    assert report.blocked == 0
    assert report.good_false_flags == 0
    assert report.needs_review_cases == 1
    assert report.needs_review_rate == 1 / 3
    assert report.override_rate is None
    assert report.kill_criteria_passed is True
    assert dict(report.criteria)["caught"] is True
    assert dict(report.criteria)["hard_fail"] is True


def test_missing_dimension_is_inconclusive_and_fails_kill_criteria():
    report = evaluate(
        _eval_set(
            require_each_dimension=True,
            expected_failures=[{"case": "B2", "dimension": "AC alignment"}],
        ),
        system_one=_system_one({"ac_3": JevAnswer(0.1)}),
    )

    assert report.kill_criteria_passed is False
    assert dict(report.criteria)["each_dimension"] is False
    assert "inconclusive" in render_eval_report(report)


def test_render_report_includes_override_as_not_available():
    report = evaluate(
        _eval_set(),
        system_one=_system_one(
            {
                "step_2_1_continuity": JevAnswer(0.1),
                "ac_3": JevAnswer(0.6),
            }
        ),
    )

    text = render_eval_report(report)

    assert "**Override rate:** n/a" in text
    assert "**Kill criteria:** PASS" in text
    assert "| B1 |" in text
    assert "Hard fail" in text


def test_load_v3_fixture():
    eval_set = load_eval_set(_FIXTURES)

    assert [case.id for case in eval_set.cases] == ["G1", "G2", "B1", "B2", "B3", "B4"]
    assert len(eval_set.expected_failures) == 4
    assert eval_set.kill_criteria.caught_min == 3
