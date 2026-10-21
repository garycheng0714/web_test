import argparse
import sys
from dataclasses import replace

from web_test.planning.review.eval_report import (
    CaseEvaluation,
    DimensionTally,
    EvalReport,
    ExpectedCheckResult,
    render_eval_report,
)
from web_test.planning.review.eval_set import EvalSet, load_eval_set
from web_test.planning.review.jev import SystemOne, typesafe_system_one
from web_test.planning.review.questions import (
    STEP_QUALITY_DIMENSIONS,
    ac_id,
    case_key,
    step_id,
)
from web_test.planning.review.service import run_review_on
from web_test.planning.review.subject import ReviewCase, ReviewStep, ReviewSubject
from web_test.planning.review.verification import (
    CheckDimension,
    CheckOutcome,
    VerificationStatus,
)


def _subject(eval_set: EvalSet) -> ReviewSubject:
    return ReviewSubject(
        prd=eval_set.prd,
        cases=[
            ReviewCase(
                index=index,
                requirement_ids=case.requirement_ids,
                module_feature="",
                test_scenario=case.scenario,
                preconditions=case.preconditions,
                steps=[
                    ReviewStep(
                        index=step_index,
                        action=step.action,
                        expected_result=step.expected_result,
                    )
                    for step_index, step in enumerate(case.steps, start=1)
                ],
            )
            for index, case in enumerate(eval_set.cases, start=1)
        ],
    )


def _case_checks(case: ReviewCase) -> list[str]:
    ids = [ac_id(case.index)]
    for step in case.steps:
        ids.extend(
            step_id(case.index, step.index, dimension)
            for dimension in STEP_QUALITY_DIMENSIONS
        )
    return ids


def _check_result(
    question_id: str,
    dimension: CheckDimension,
    by_id: dict[str, CheckOutcome],
) -> ExpectedCheckResult:
    check = by_id.get(question_id)
    return ExpectedCheckResult(
        question_id=question_id,
        dimension=dimension,
        status=check.status if check is not None else VerificationStatus.BLOCKED,
        probability=check.probability if check is not None else None,
    )


def evaluate(
    eval_set: EvalSet,
    *,
    system_one: SystemOne,
) -> EvalReport:
    subject = _subject(eval_set)
    record = run_review_on(
        subject,
        eval_set.model_dump_json(),
        system_one=system_one,
    )
    checks = {check.question_id: check for check in record.result.checks}
    case_status = {case.key: case.status for case in record.result.cases}
    case_results = []
    for index, eval_case in enumerate(eval_set.cases, start=1):
        review_case = subject.cases[index - 1]
        expected = []
        for failure in eval_set.expected_failures:
            if failure.case != eval_case.id:
                continue
            question_id = (
                ac_id(index)
                if failure.step is None
                else step_id(index, failure.step, failure.dimension)
            )
            expected.append(_check_result(question_id, failure.dimension, checks))

        false_flags = ()
        if eval_case.label == "good":
            false_flags = tuple(
                checks[question_id]
                for question_id in _case_checks(review_case)
                if checks[question_id].status is not VerificationStatus.PASS
            )

        case_results.append(
            CaseEvaluation(
                case_id=eval_case.id,
                label=eval_case.label,
                tests=eval_case.tests,
                scenario=eval_case.scenario,
                status=case_status[case_key(index)],
                expected=tuple(expected),
                false_flags=false_flags,
            )
        )

    expected_results = [
        result for case in case_results if case.label == "bad" for result in case.expected
    ]
    caught = sum(
        result.status in {VerificationStatus.FAIL, VerificationStatus.NEEDS_REVIEW}
        for result in expected_results
    )
    hard_fail = sum(result.status is VerificationStatus.FAIL for result in expected_results)
    blocked = sum(result.status is VerificationStatus.BLOCKED for result in expected_results)
    good_false_flags = sum(len(case.false_flags) for case in case_results if case.label == "good")
    needs_review_cases = sum(
        case.status is VerificationStatus.NEEDS_REVIEW for case in case_results
    )

    dimensions = []
    for dimension in CheckDimension:
        expected_for_dimension = [
            result for result in expected_results if result.dimension is dimension
        ]
        false_flags_for_dimension = sum(
            1
            for case in case_results
            if case.label == "good"
            for check in case.false_flags
            if check.dimension is dimension
        )
        dimensions.append(
            DimensionTally(
                dimension=dimension,
                expected=len(expected_for_dimension),
                caught=sum(
                    result.status
                    in {VerificationStatus.FAIL, VerificationStatus.NEEDS_REVIEW}
                    for result in expected_for_dimension
                ),
                hard_fail=sum(
                    result.status is VerificationStatus.FAIL
                    for result in expected_for_dimension
                ),
                false_flags=false_flags_for_dimension,
            )
        )

    criteria = (
        ("caught", caught >= eval_set.kill_criteria.caught_min),
        ("hard_fail", hard_fail >= eval_set.kill_criteria.hard_fail_min),
        (
            "good_false_flags",
            good_false_flags <= eval_set.kill_criteria.good_false_flags_max,
        ),
        ("bad_blocked", blocked <= eval_set.kill_criteria.bad_blocked_max),
        (
            "each_dimension",
            not eval_set.kill_criteria.require_each_dimension
            or all(dimension.expected > 0 for dimension in dimensions),
        ),
    )

    return EvalReport(
        model=record.binding.model,
        question_set_version=record.binding.question_set_version,
        record_status=record.result.status,
        cases=tuple(case_results),
        dimensions=tuple(dimensions),
        caught=caught,
        expected=len(expected_results),
        hard_fail=hard_fail,
        blocked=blocked,
        needs_review_cases=needs_review_cases,
        needs_review_rate=needs_review_cases / len(case_results) if case_results else 0.0,
        good_false_flags=good_false_flags,
        override_rate=None,
        criteria=criteria,
        kill_criteria_passed=all(passed for _, passed in criteria),
    )


def _signature(report: EvalReport) -> tuple[object, ...]:
    return (
        tuple((case.case_id, case.status) for case in report.cases),
        tuple(
            (case.case_id, tuple(check.question_id for check in case.false_flags))
            for case in report.cases
        ),
        tuple(
            (case.case_id, tuple((result.question_id, result.status) for result in case.expected))
            for case in report.cases
            if case.label == "bad"
        ),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="review-eval", description="Evaluate the Jev verifier.")
    parser.add_argument(
        "--fixtures",
        default="tests/fixtures/review_eval/register_login_golden_v1.json",
        help="path to the eval fixture JSON",
    )
    parser.add_argument("--runs", type=int, default=1, help="number of runs (default: 1)")
    args = parser.parse_args(argv)
    if args.runs < 1:
        print("failed: --runs must be at least 1", file=sys.stderr)
        return 1

    try:
        eval_set = load_eval_set(args.fixtures)
        reports = [
            evaluate(eval_set, system_one=typesafe_system_one)
            for _ in range(args.runs)
        ]
    except (OSError, ValueError) as error:
        print(f"failed: {error}", file=sys.stderr)
        return 1

    report = reports[0]
    if len(reports) > 1:
        first = _signature(report)
        report = replace(
            report,
            runs=len(reports),
            reproduced=all(_signature(item) == first for item in reports[1:]),
        )

    print(render_eval_report(report))
    return 0 if report.kill_criteria_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
